"""
Pattern-Aware Code Generator Module

Generates code with pattern awareness based on context and pattern library.
Uses real LLM (Anthropic Claude) for intelligent code generation.
"""

import ast
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from metrics.llm_providers import LLMManager, get_llm_manager

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of code validation."""

    is_valid: bool
    syntax_valid: bool
    compilation_error: Optional[str]
    warnings: List[str]


@dataclass
class GenerationResult:
    """Result of code generation."""

    code: str
    patterns_applied: List[Dict[str, Any]]
    patterns_suggested: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    report: str
    confidence: float
    validation: Optional[ValidationResult] = None


class PatternAwareGenerator:
    """Generates code with pattern awareness using real LLM."""

    def __init__(
        self,
        pattern_library: List[Dict[str, Any]],
        pattern_library_version: str = "1.0.0",
        use_llm: bool = True,
        api_key: Optional[str] = None,
        llm_provider: Optional[str] = None,
    ):
        """Initialize the pattern-aware code generator.

        Args:
            pattern_library: List of patterns from PatternManager
            pattern_library_version: Version of the pattern library
            use_llm: Whether to use LLM for generation (default: True)
            api_key: API key (deprecated - use environment variables)
            llm_provider: Preferred LLM provider ("claude", "openai", "gemini")
        """
        self.pattern_library = pattern_library
        self.pattern_library_version = pattern_library_version
        self.use_llm = use_llm
        self.llm_manager = None

        # Initialize LLM manager if using LLM
        if self.use_llm:
            try:
                self.llm_manager = get_llm_manager()
                if llm_provider:
                    self.llm_manager.preferred_provider = llm_provider

                if self.llm_manager.is_any_available():
                    providers = self.llm_manager.list_available_providers()
                    logger.info(f"LLM manager initialized with providers: {providers}")
                else:
                    logger.warning(
                        "No LLM providers available, falling back to template mode"
                    )
                    self.use_llm = False
            except Exception as e:
                logger.warning(
                    f"Could not initialize LLM manager: {e}, falling back to template mode"
                )
                self.use_llm = False

    def generate(
        self,
        prompt: str,
        metrics_context: Optional[Dict[str, Any]] = None,
        apply_patterns: bool = True,
        min_confidence: float = 0.8,
        validate: bool = True,
    ) -> GenerationResult:
        """Generate code with pattern awareness.

        Args:
            prompt: User prompt for code generation
            metrics_context: Optional metrics context from analyzer
            apply_patterns: Whether to apply patterns automatically
            min_confidence: Minimum confidence score to apply patterns
            validate: Whether to validate generated code

        Returns:
            GenerationResult with code and metadata
        """
        # Analyze prompt for context indicators
        context_indicators = self._analyze_prompt(prompt)

        # Match patterns based on context
        matched_patterns = self._match_patterns(context_indicators, metrics_context)

        # Apply patterns by severity
        patterns_to_apply, patterns_to_suggest = self._prioritize_patterns(
            matched_patterns, apply_patterns, min_confidence
        )

        # Generate code with pattern annotations
        if self.use_llm and self.llm_manager:
            code = self._generate_code_with_llm(
                prompt, patterns_to_apply, patterns_to_suggest, metrics_context
            )
        else:
            code = self._generate_code_with_templates(
                prompt, patterns_to_apply, patterns_to_suggest
            )

        # Validate code if requested
        validation_result = None
        if validate:
            validation_result = self._validate_code(code)

        # Calculate overall confidence
        confidence = self._calculate_confidence(matched_patterns)

        # Adjust confidence based on validation
        if validation_result and not validation_result.is_valid:
            confidence = confidence * 0.5  # Reduce confidence for invalid code

        # Generate metadata
        metadata = {
            "prompt": prompt,
            "pattern_library_version": self.pattern_library_version,
            "timestamp": datetime.now().isoformat(),
            "confidence": float(confidence),
            "context_indicators": context_indicators,
            "use_llm": self.use_llm,
        }

        # Generate report
        report = self._generate_report(
            patterns_to_apply,
            patterns_to_suggest,
            context_indicators,
            confidence,
            validation_result,
        )

        logger.debug(f"Generated code with {len(patterns_to_apply)} patterns applied")

        return GenerationResult(
            code=code,
            patterns_applied=patterns_to_apply,
            patterns_suggested=patterns_to_suggest,
            metadata=metadata,
            report=report,
            confidence=confidence,
            validation=validation_result,
        )

    def _analyze_prompt(self, prompt: str) -> Dict[str, bool]:
        """Analyze prompt for context indicators.

        Args:
            prompt: User prompt

        Returns:
            Dictionary of context indicators
        """
        prompt_lower = prompt.lower()

        indicators = {
            "numpy": "numpy" in prompt_lower
            or "np." in prompt_lower
            or "array" in prompt_lower,
            "json": "json" in prompt_lower
            or "api" in prompt_lower
            or "serialize" in prompt_lower,
            "list_access": "list" in prompt_lower
            or "array" in prompt_lower
            or "first" in prompt_lower,
            "exception": "exception" in prompt_lower
            or "error" in prompt_lower
            or "try" in prompt_lower,
            "logging": "log" in prompt_lower
            or "debug" in prompt_lower
            or "print" in prompt_lower,
            "file": "file" in prompt_lower
            or "temp" in prompt_lower
            or "upload" in prompt_lower,
            "large_file": "large" in prompt_lower
            or "audio" in prompt_lower
            or "upload" in prompt_lower,
            "categorization": "categorize" in prompt_lower
            or "classify" in prompt_lower,
            "fastapi": "fastapi" in prompt_lower
            or "endpoint" in prompt_lower
            or "api" in prompt_lower,
        }

        return indicators

    def _match_patterns(
        self,
        context_indicators: Dict[str, bool],
        metrics_context: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Match patterns based on context.

        Args:
            context_indicators: Context indicators from prompt analysis
            metrics_context: Metrics context from analyzer

        Returns:
            List of matched patterns with confidence scores
        """
        matched = []

        # Pattern matching rules
        pattern_rules = {
            "numpy_json_serialization": ["numpy", "json"],
            "bounds_checking": ["list_access"],
            "specific_exceptions": ["exception"],
            "logger_debug": ["logging"],
            "metadata_categorization": ["categorization"],
            "temp_file_handling": ["file"],
            "large_file_processing": ["large_file", "file"],
        }

        # Check each pattern
        for pattern in self.pattern_library:
            pattern_name = pattern.get("name", "")
            rules = pattern_rules.get(pattern_name, [])

            # Calculate match score
            match_score = 0.0
            if rules:
                matches = sum(
                    1 for rule in rules if context_indicators.get(rule, False)
                )
                match_score = matches / len(rules)

            # Boost score if pattern appears in metrics context
            if metrics_context:
                high_freq = metrics_context.get("high_frequency_patterns", [])
                critical = metrics_context.get("critical_patterns", [])

                if pattern_name in critical:
                    match_score = min(1.0, match_score + 0.3)
                elif pattern_name in high_freq:
                    match_score = min(1.0, match_score + 0.2)

            if match_score > 0:
                matched.append(
                    {
                        "pattern": pattern,
                        "confidence": float(match_score),
                        "severity": pattern.get("severity", "medium"),
                    }
                )

        # Sort by confidence descending
        matched.sort(key=lambda x: x["confidence"], reverse=True)

        return matched

    def _prioritize_patterns(
        self,
        matched_patterns: List[Dict[str, Any]],
        apply_patterns: bool,
        min_confidence: float,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Prioritize patterns by severity and confidence.

        Args:
            matched_patterns: Matched patterns with confidence
            apply_patterns: Whether to apply patterns
            min_confidence: Minimum confidence to apply

        Returns:
            Tuple of (patterns_to_apply, patterns_to_suggest)
        """
        to_apply = []
        to_suggest = []

        if not apply_patterns:
            return [], matched_patterns

        severity_rules = {
            "critical": True,  # Always apply
            "high": True,  # Apply by default
            "medium": True,  # Apply with notice
            "low": False,  # Suggest only
        }

        for match in matched_patterns:
            pattern = match["pattern"]
            confidence = match["confidence"]
            severity = match["severity"]

            should_apply = severity_rules.get(severity, False)
            meets_confidence = confidence >= min_confidence

            if should_apply and meets_confidence:
                to_apply.append(match)
            else:
                to_suggest.append(match)

        return to_apply, to_suggest

    def _generate_code_with_llm(
        self,
        prompt: str,
        patterns_to_apply: List[Dict[str, Any]],
        patterns_to_suggest: List[Dict[str, Any]],
        metrics_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate code using LLM with pattern context.

        Args:
            prompt: Original prompt
            patterns_to_apply: Patterns to apply
            patterns_to_suggest: Patterns to suggest
            metrics_context: Optional metrics context

        Returns:
            Generated code
        """
        # Build enriched prompt with pattern context
        enriched_prompt = self._build_enriched_prompt(
            prompt, patterns_to_apply, patterns_to_suggest, metrics_context
        )

        try:
            # Use LLM manager for generation
            response = self.llm_manager.generate(
                enriched_prompt, max_tokens=4096, fallback=True
            )

            # Extract code from response
            code = self._extract_code_from_response(response.text)

            return code

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Fall back to template mode
            return self._generate_code_with_templates(
                prompt, patterns_to_apply, patterns_to_suggest
            )

    def _build_enriched_prompt(
        self,
        prompt: str,
        patterns_to_apply: List[Dict[str, Any]],
        patterns_to_suggest: List[Dict[str, Any]],
        metrics_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build enriched prompt with pattern context.

        Args:
            prompt: Original prompt
            patterns_to_apply: Patterns to apply
            patterns_to_suggest: Patterns to suggest
            metrics_context: Optional metrics context

        Returns:
            Enriched prompt string
        """
        enriched = f"{prompt}\n\n"

        enriched += "## Required Patterns\n"
        enriched += "Apply the following validated patterns to your code:\n\n"

        if patterns_to_apply:
            for match in patterns_to_apply:
                pattern = match["pattern"]
                pattern_name = pattern["name"]
                description = pattern.get("description", "")
                good_example = pattern.get("good_example", "")
                effectiveness = pattern.get("effectiveness_score", 0.5)

                enriched += f"### Pattern: {pattern_name}\n"
                enriched += f"**Effectiveness:** {effectiveness:.1%}\n"
                enriched += f"**Description:** {description}\n"

                if good_example:
                    enriched += f"**Example:**\n```python\n{good_example}\n```\n"

                enriched += "\n"
        else:
            enriched += "No specific patterns required.\n\n"

        if patterns_to_suggest:
            enriched += "\n## Suggested Patterns\n"
            enriched += "Consider these patterns if applicable:\n\n"

            for match in patterns_to_suggest:
                pattern = match["pattern"]
                pattern_name = pattern["name"]
                description = pattern.get("description", "")
                enriched += f"- **{pattern_name}**: {description}\n"

            enriched += "\n"

        if metrics_context:
            enriched += "\n## Metrics Context\n"
            high_freq = metrics_context.get("high_frequency_patterns", [])
            if high_freq:
                enriched += f"High-frequency issues: {', '.join(high_freq[:5])}\n"

        enriched += "\n## Instructions\n"
        enriched += "Generate production-ready Python code that:\n"
        enriched += "1. Implements the requested functionality\n"
        enriched += "2. Applies all required patterns\n"
        enriched += "3. Includes proper error handling\n"
        enriched += "4. Has clear comments explaining pattern usage\n"
        enriched += "5. Is syntactically correct and ready to run\n"

        return enriched

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from LLM response.

        Args:
            response: Raw LLM response

        Returns:
            Cleaned code
        """
        # Remove markdown code blocks
        if "```python" in response:
            parts = response.split("```python")
            if len(parts) > 1:
                code_part = parts[1].split("```")[0]
                return code_part.strip()

        if "```" in response:
            parts = response.split("```")
            if len(parts) > 1:
                return parts[1].strip()

        return response.strip()

    def _generate_code_with_templates(
        self,
        prompt: str,
        patterns_to_apply: List[Dict[str, Any]],
        patterns_to_suggest: List[Dict[str, Any]],
    ) -> str:
        """Generate code with pattern annotations.

        Args:
            prompt: Original prompt
            patterns_to_apply: Patterns to apply
            patterns_to_suggest: Patterns to suggest

        Returns:
            Generated code with annotations
        """
        # Start with header comment
        code_lines = [
            '"""',
            f"Generated code for: {prompt}",
            "",
            "Pattern-aware code generation applied the following patterns:",
        ]

        # List applied patterns
        if patterns_to_apply:
            for match in patterns_to_apply:
                pattern_name = match["pattern"]["name"]
                confidence = match["confidence"]
                code_lines.append(f"  - {pattern_name} (confidence: {confidence:.2f})")
        else:
            code_lines.append("  - None")

        code_lines.append('"""')
        code_lines.append("")

        # Generate imports based on patterns
        imports = self._generate_imports(patterns_to_apply)
        code_lines.extend(imports)
        code_lines.append("")

        # Generate main code based on prompt and patterns
        main_code = self._generate_main_code(prompt, patterns_to_apply)
        code_lines.extend(main_code)

        # Add suggestions as comments
        if patterns_to_suggest:
            code_lines.append("")
            code_lines.append("# SUGGESTED PATTERNS (not auto-applied):")
            for match in patterns_to_suggest:
                pattern_name = match["pattern"]["name"]
                description = match["pattern"]["description"]
                code_lines.append(f"# - {pattern_name}: {description[:80]}...")

        return "\n".join(code_lines)

    def _generate_imports(self, patterns_to_apply: List[Dict[str, Any]]) -> List[str]:
        """Generate import statements based on patterns.

        Args:
            patterns_to_apply: Patterns being applied

        Returns:
            List of import statement strings
        """
        imports = set()

        pattern_imports = {
            "numpy_json_serialization": ["import json", "import numpy as np"],
            "bounds_checking": ["import logging"],
            "specific_exceptions": ["import json", "import logging"],
            "logger_debug": ["import logging"],
            "temp_file_handling": ["import os", "import tempfile", "import logging"],
            "large_file_processing": ["import os", "import logging"],
        }

        for match in patterns_to_apply:
            pattern_name = match["pattern"]["name"]
            pattern_imports_list = pattern_imports.get(pattern_name, [])
            imports.update(pattern_imports_list)

        return sorted(list(imports))

    def _generate_main_code(
        self, prompt: str, patterns_to_apply: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate main code based on prompt and patterns.

        Args:
            prompt: Original prompt
            patterns_to_apply: Patterns being applied

        Returns:
            List of code lines
        """
        code_lines = []

        # Check if logger pattern is applied
        uses_logging = any(
            p["pattern"]["name"]
            in ["logger_debug", "bounds_checking", "specific_exceptions"]
            for p in patterns_to_apply
        )

        if uses_logging:
            code_lines.append("logger = logging.getLogger(__name__)")
            code_lines.append("")

        # Generate function based on prompt keywords
        prompt_lower = prompt.lower()

        if "numpy" in prompt_lower and "json" in prompt_lower:
            code_lines.extend(self._generate_numpy_json_function())
        elif "list" in prompt_lower or "first" in prompt_lower:
            code_lines.extend(self._generate_list_access_function())
        elif "file" in prompt_lower:
            code_lines.extend(self._generate_file_processing_function())
        else:
            # Generic function template
            code_lines.extend(
                [
                    "def process_data(data):",
                    '    """Process data according to requirements."""',
                    "    # Pattern-aware template: Customize the logic below for your specific use case",
                    (
                        '    logger.debug(f"Processing data: {data}")'
                        if uses_logging
                        else "    pass"
                    ),
                    "    return data",
                ]
            )

        return code_lines

    def _generate_numpy_json_function(self) -> List[str]:
        """Generate NumPy to JSON function with pattern."""
        return [
            "def process_numpy_data(data_array):",
            '    """Process NumPy array and return JSON-serializable result."""',
            "    # PATTERN: numpy_json_serialization - Convert before JSON serialization",
            "    result = {",
            '        "mean": float(np.mean(data_array)),',
            '        "std": float(np.std(data_array)),',
            '        "max": float(np.max(data_array))',
            "    }",
            "    return json.dumps(result)",
        ]

    def _generate_list_access_function(self) -> List[str]:
        """Generate list access function with bounds checking."""
        return [
            "def get_first_item(items):",
            '    """Get first item with bounds checking."""',
            "    # PATTERN: bounds_checking - Validate before accessing",
            "    if not items:",
            '        logger.debug("List is empty, returning None")',
            "        return None",
            "    return items[0]",
        ]

    def _generate_file_processing_function(self) -> List[str]:
        """Generate file processing function with pattern."""
        return [
            "def process_file(file_path, max_size_bytes=800 * 1024 * 1024):",
            '    """Process file with size validation."""',
            "    # PATTERN: large_file_processing - Check size before loading",
            "    try:",
            "        file_size = os.path.getsize(file_path)",
            "        ",
            "        if file_size > max_size_bytes:",
            '            logger.debug(f"File too large: {file_size} > {max_size_bytes}")',
            "            return None",
            "        ",
            "        return {",
            '            "file_path": file_path,',
            '            "size_bytes": int(file_size)',
            "        }",
            "    except (FileNotFoundError, IOError, OSError) as e:",
            '        logger.debug(f"Error processing file: {e}")',
            "        return None",
        ]

    def _validate_code(self, code: str) -> ValidationResult:
        """Validate generated code.

        Args:
            code: Generated code to validate

        Returns:
            ValidationResult with validation details
        """
        warnings = []
        syntax_valid = False
        compilation_error = None

        # Check syntax
        try:
            ast.parse(code)
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            compilation_error = f"Syntax error at line {e.lineno}: {e.msg}"
            logger.warning(f"Code validation failed: {compilation_error}")

        # Additional checks
        if syntax_valid:
            # Check for common issues
            if "print(" in code:
                warnings.append(
                    "Code contains print() statements - consider using logger.debug()"
                )

            if "except:" in code and "except Exception:" not in code:
                warnings.append("Code contains bare except: - use specific exceptions")

            # Check for TODO comments
            if "TODO" in code or "FIXME" in code:
                warnings.append("Code contains TODO/FIXME comments")

        is_valid = syntax_valid and len(warnings) == 0

        return ValidationResult(
            is_valid=is_valid,
            syntax_valid=syntax_valid,
            compilation_error=compilation_error,
            warnings=warnings,
        )

    def _calculate_confidence(self, matched_patterns: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score.

        Args:
            matched_patterns: Matched patterns with confidence scores

        Returns:
            Overall confidence score
        """
        if not matched_patterns:
            return 0.5

        # Average of top 3 confidence scores
        top_scores = sorted([m["confidence"] for m in matched_patterns], reverse=True)[
            :3
        ]

        return sum(top_scores) / len(top_scores) if top_scores else 0.5

    def _generate_report(
        self,
        patterns_applied: List[Dict[str, Any]],
        patterns_suggested: List[Dict[str, Any]],
        context_indicators: Dict[str, bool],
        confidence: float,
        validation: Optional[ValidationResult] = None,
    ) -> str:
        """Generate human-readable report.

        Args:
            patterns_applied: Patterns that were applied
            patterns_suggested: Patterns that were suggested
            context_indicators: Context detected from prompt
            confidence: Overall confidence score
            validation: Optional validation results

        Returns:
            Report string
        """
        lines = [
            "=== Pattern-Aware Code Generation Report ===",
            "",
            f"Confidence Score: {confidence:.2%}",
            f"Generation Mode: {'LLM' if self.use_llm and self.llm_manager else 'Template'}",
            "",
            "Context Detected:",
        ]

        for indicator, detected in context_indicators.items():
            if detected:
                lines.append(f"  ✓ {indicator}")

        lines.append("")
        lines.append(f"Patterns Applied: {len(patterns_applied)}")
        for match in patterns_applied:
            pattern_name = match["pattern"]["name"]
            pattern_confidence = match["confidence"]
            severity = match["severity"]
            lines.append(
                f"  - {pattern_name} (severity: {severity}, confidence: {pattern_confidence:.2%})"
            )

        lines.append("")
        lines.append(f"Patterns Suggested: {len(patterns_suggested)}")
        for match in patterns_suggested:
            pattern_name = match["pattern"]["name"]
            pattern_confidence = match["confidence"]
            lines.append(f"  - {pattern_name} (confidence: {pattern_confidence:.2%})")

        # Add validation results
        if validation:
            lines.append("")
            lines.append("Validation Results:")
            lines.append(f"  Syntax Valid: {'✓' if validation.syntax_valid else '✗'}")

            if validation.compilation_error:
                lines.append(f"  Error: {validation.compilation_error}")

            if validation.warnings:
                lines.append(f"  Warnings: {len(validation.warnings)}")
                for warning in validation.warnings:
                    lines.append(f"    - {warning}")

            lines.append(
                f"  Overall: {'✓ Valid' if validation.is_valid else '✗ Issues Found'}"
            )

        lines.append("")
        lines.append("=== End Report ===")

        return "\n".join(lines)
