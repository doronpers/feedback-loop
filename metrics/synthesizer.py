"""
Code Synthesizer Module

Generates multiple code candidates using different strategies and synthesizes
them into an optimal version.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from metrics.code_generator import PatternAwareGenerator, GenerationResult

logger = logging.getLogger(__name__)


@dataclass
class SynthesisResult:
    """Result of code synthesis."""
    final_code: str
    candidates: List[GenerationResult]
    report: str
    synthesis_logic: str


class CodeSynthesizer:
    """Synthesizes optimal code from multiple generated candidates."""

    def __init__(self, generator: PatternAwareGenerator):
        """Initialize the synthesizer.
        
        Args:
            generator: Initialized PatternAwareGenerator instance
        """
        self.generator = generator

    def synthesize(
        self,
        prompt: str,
        num_candidates: int = 3,
        metrics_context: Optional[Dict[str, Any]] = None,
        input_files: Optional[List[str]] = None
    ) -> SynthesisResult:
        """Generate candidates and synthesize the best code.
        
        Args:
            prompt: User prompt
            num_candidates: Number of variations to generate (ignored if input_files provided)
            metrics_context: Optional metrics context
            input_files: Optional list of file paths to use as candidates
            
        Returns:
            SynthesisResult
        """
        logger.info(f"Synthesizing code for: {prompt}")
        
        candidates: List[GenerationResult] = []
        
        # If input files are provided, use those as candidates
        if input_files:
            logger.info(f"Using {len(input_files)} input files as candidates")
            candidates = self._load_candidates_from_files(input_files)
        else:
            # Generate Candidates with different "personas" or focus areas
            logger.info(f"Generating {num_candidates} candidates")
            candidates = self._generate_candidates(prompt, num_candidates, metrics_context)

        # 2. Synthesize using LLM
        if self.generator.use_llm and self.generator.llm_manager:
            final_code, logic = self._synthesize_with_llm(prompt, candidates)
        else:
            # Fallback for template mode: just pick the best valid one or the first one
            final_code, logic = self._synthesize_fallback(candidates)

        # 3. Generate Report
        report = self._generate_synthesis_report(candidates, logic)

        return SynthesisResult(
            final_code=final_code,
            candidates=candidates,
            report=report,
            synthesis_logic=logic
        )

    def _load_candidates_from_files(self, file_paths: List[str]) -> List[GenerationResult]:
        """Load code from files and create GenerationResult objects."""
        from metrics.code_generator import GenerationResult, ValidationResult
        
        candidates = []
        for i, file_path in enumerate(file_paths):
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                
                # Validate the code
                validation = self.generator._validate_code(code)
                
                # Create a GenerationResult for this file
                result = GenerationResult(
                    code=code,
                    patterns_applied=[],
                    patterns_suggested=[],
                    metadata={
                        "strategy": f"User File {i+1}",
                        "source_file": file_path,
                        "prompt": f"Loaded from {file_path}"
                    },
                    report=f"Loaded from file: {file_path}",
                    confidence=0.8 if validation.is_valid else 0.5,
                    validation=validation
                )
                candidates.append(result)
                logger.debug(f"Loaded candidate from {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                
        return candidates

    def _generate_candidates(
        self,
        prompt: str,
        num_candidates: int,
        metrics_context: Optional[Dict[str, Any]]
    ) -> List[GenerationResult]:
        """Generate multiple code candidates with different strategies."""
        strategies = [
            ("Robust", "Focus on error handling, edge cases, and logging."),
            ("Performant", "Focus on execution speed, memory usage, and efficiency."),
            ("Concise", "Focus on clean, pythonic, and minimal code.")
        ]
        
        # Ensure we have enough strategies (cycle if needed)
        while len(strategies) < num_candidates:
            strategies.append(strategies[len(strategies) % 3])
            
        candidates = []
        
        for i in range(num_candidates):
            strategy_name, strategy_inst = strategies[i]
            logger.debug(f"Generating candidate {i+1}: {strategy_name}")
            
            # Augment prompt with strategy
            augmented_prompt = (
                f"{prompt}\n\n"
                f"STRATEGY: {strategy_name}\n"
                f"INSTRUCTION: {strategy_inst}"
            )
            
            # Generate code
            result = self.generator.generate(
                augmented_prompt,
                metrics_context=metrics_context,
                apply_patterns=True,
                validate=True
            )
            
            # Tag the result with its strategy
            result.metadata["strategy"] = strategy_name
            candidates.append(result)
            
        return candidates

    def _synthesize_with_llm(
        self, 
        prompt: str, 
        candidates: List[GenerationResult]
    ) -> tuple[str, str]:
        """Use LLM to merge candidates into the best version."""
        
        synthesis_prompt = f"""
You are a Lead Senior Software Engineer. I need you to synthesize the best possible code implementation from multiple candidate solutions.

ORIGINAL REQUEST:
{prompt}

CANDIDATE SOLUTIONS:

"""
        for i, cand in enumerate(candidates):
            strategy = cand.metadata.get("strategy", "Unknown")
            synthesis_prompt += f"--- CANDIDATE {i+1} ({strategy}) ---\n"
            synthesis_prompt += f"{cand.code}\n\n"

        synthesis_prompt += """
INSTRUCTIONS:
1. Analyze the strengths and weaknesses of each candidate.
2. Combine the best parts of each into a SINGLE, OPTIMAL implementation.
3. Ensure the final code is robust, performant, and clean.
4. If one candidate is clearly superior, you can use it as the base but improve it.
5. EXPLAIN your synthesis logic briefly before the code.

OUTPUT FORMAT:
[Logic and Reasoning]
... your explanation here ...

[Final Code]
```python
... your code here ...
```
"""
        
        try:
            response = self.generator.llm_manager.generate(
                synthesis_prompt,
                max_tokens=4096
            )
            text = response.text
            
            # Extract Logic and Code
            logic = "Logic not parsed."
            code = text
            
            if "[Final Code]" in text:
                parts = text.split("[Final Code]")
                logic = parts[0].replace("[Logic and Reasoning]", "").strip()
                code_part = parts[1]
                code = self.generator._extract_code_from_response(code_part)
            else:
                # Fallback extraction
                code = self.generator._extract_code_from_response(text)
                logic = text.split("```")[0].strip()
                
            return code, logic

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return self._synthesize_fallback(candidates)

    def _synthesize_fallback(self, candidates: List[GenerationResult]) -> tuple[str, str]:
        """Fallback synthesis: pick the valid candidate with highest confidence."""
        best_cand = max(candidates, key=lambda x: (x.validation.is_valid if x.validation else False, x.confidence))
        strategy = best_cand.metadata.get("strategy", "Unknown")
        return best_cand.code, f"Fallback: Selected best candidate ({strategy}) based on validation and confidence."

    def _generate_synthesis_report(
        self, 
        candidates: List[GenerationResult], 
        logic: str
    ) -> str:
        """Generate a user-facing report of the synthesis process."""
        lines = [
            "=== Code Synthesis Report ===",
            "",
            f"Generated {len(candidates)} candidates:",
        ]
        
        for i, cand in enumerate(candidates):
            strategy = cand.metadata.get("strategy", "Unknown")
            valid_icon = "✓" if cand.validation and cand.validation.is_valid else "✗"
            lines.append(f"  {i+1}. {strategy}: {valid_icon} Valid (Confidence: {cand.confidence:.2f})")
            
        lines.append("")
        lines.append("Synthesis Logic:")
        lines.append(logic)
        lines.append("")
        lines.append("=== End Report ===")
        
        return "\n".join(lines)
