"""
Plan Parser Module

Parses markdown plan files (task_plan.md, notes.md) to extract pattern references
and task context for integration with feedback-loop's pattern system.

This module implements concepts from Planning with Files:
- Original work: https://github.com/OthmanAdi/planning-with-files
- Author: Ahmad Othman Ammar Adi (OthmanAdi)
- License: MIT License

Adapted and extended for feedback-loop integration.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PlanParser:
    """Parses Planning with Files style markdown plan files."""
    
    def __init__(self):
        """Initialize the plan parser."""
        pass
    
    def parse_task_plan(self, plan_path: str) -> Dict[str, Any]:
        """Parse task_plan.md to extract goal, phases, patterns, and metadata.
        
        Args:
            plan_path: Path to the task_plan.md file
            
        Returns:
            Dictionary containing:
                - goal: Task goal/objective
                - phases: List of phases with status
                - patterns: List of pattern references
                - current_phase: Currently active phase
                - metadata: Additional metadata (timestamps, etc.)
                
        Raises:
            FileNotFoundError: If plan file doesn't exist
            ValueError: If plan file cannot be parsed
        """
        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")
        
        content = plan_file.read_text()
        
        return {
            "goal": self._extract_goal(content),
            "phases": self._extract_phases(content),
            "patterns": self.extract_pattern_references(content),
            "current_phase": self._extract_current_phase(content),
            "metadata": {
                "plan_path": str(plan_file.resolve()),
                "plan_name": plan_file.name
            }
        }
    
    def extract_task_context(self, plan_path: str) -> Dict[str, Any]:
        """Get task goal, current phase, and deliverables from plan file.
        
        Args:
            plan_path: Path to the task_plan.md file
            
        Returns:
            Dictionary with task context:
                - goal: Task goal
                - current_phase: Current phase name
                - phase_status: Status of current phase
                - deliverables: List of deliverables
        """
        parsed = self.parse_task_plan(plan_path)
        
        current_phase_info = None
        for phase in parsed["phases"]:
            if phase.get("is_current", False):
                current_phase_info = phase
                break
        
        return {
            "goal": parsed["goal"],
            "current_phase": parsed["current_phase"],
            "phase_status": current_phase_info.get("status") if current_phase_info else None,
            "deliverables": self._extract_deliverables(parsed.get("phases", []))
        }
    
    def extract_pattern_references(self, content: str) -> List[str]:
        """Find pattern names mentioned in plan content.
        
        Looks for "## Patterns to Apply" section with checkboxes.
        
        Args:
            content: Markdown content of the plan file
            
        Returns:
            List of pattern names found in the content
        """
        patterns = []
        in_patterns_section = False
        found_patterns_section = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            # Check for patterns section
            if stripped.startswith("##"):
                heading = stripped[2:].strip().lower()
                if "pattern" in heading and "apply" in heading:
                    in_patterns_section = True
                    found_patterns_section = True
                    continue
                elif found_patterns_section:
                    # Next section, stop
                    break
                else:
                    in_patterns_section = False
            
            if not in_patterns_section:
                continue
            
            # Match checkbox pattern: - [ ] pattern_name or - [x] pattern_name
            match = re.match(r"-\s*\[([ xX])\]\s*([^\s(]+)", stripped)
            if match:
                pattern_name = match.group(2).strip()
                # Remove trailing annotations like "(from feedback-loop)"
                pattern_name = pattern_name.split("(")[0].strip()
                if pattern_name:
                    patterns.append(pattern_name)
        
        return patterns
    
    def _extract_goal(self, content: str) -> str:
        """Extract task goal from plan file.
        
        Looks for "# Goal" or "## Goal" section, or first line after title.
        
        Args:
            content: Markdown content
            
        Returns:
            Goal text or empty string if not found
        """
        lines = content.splitlines()
        
        # Look for explicit goal section
        for i, line in enumerate(lines):
            if re.match(r"^#+\s+Goal", line, re.IGNORECASE):
                # Get next non-empty line as goal
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        return lines[j].strip()
        
        # If no explicit goal section, use first paragraph after title
        for i, line in enumerate(lines):
            if line.startswith("#") and i + 1 < len(lines):
                # Skip title, get first non-empty line
                for j in range(i + 1, len(lines)):
                    stripped = lines[j].strip()
                    if stripped and not stripped.startswith("#"):
                        return stripped
        
        return ""
    
    def _extract_phases(self, content: str) -> List[Dict[str, Any]]:
        """Extract phases from plan file.
        
        Looks for "## Phases" section with checkboxes.
        
        Args:
            content: Markdown content
            
        Returns:
            List of phase dictionaries with name, status, and is_current flag
        """
        phases = []
        in_phases_section = False
        found_phases_section = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            # Check for phases section
            if stripped.startswith("##"):
                heading = stripped[2:].strip().lower()
                if "phase" in heading:
                    in_phases_section = True
                    found_phases_section = True
                    continue
                elif found_phases_section:
                    # Next section, stop
                    break
                else:
                    in_phases_section = False
            
            if not in_phases_section:
                continue
            
            # Match checkbox pattern: - [ ] Phase name or - [x] Phase name
            match = re.match(r"-\s*\[([ xX])\]\s*(.+)", stripped)
            if match:
                checked = match.group(1).strip().lower() == "x"
                phase_name = match.group(2).strip()
                
                # Check if marked as current
                is_current = "current" in phase_name.lower() or "(current)" in phase_name.lower()
                
                phases.append({
                    "name": phase_name,
                    "status": "completed" if checked else "pending",
                    "is_current": is_current
                })
        
        return phases
    
    def _extract_current_phase(self, content: str) -> Optional[str]:
        """Extract current phase name.
        
        Args:
            content: Markdown content
            
        Returns:
            Current phase name or None
        """
        phases = self._extract_phases(content)
        for phase in phases:
            if phase.get("is_current", False):
                return phase["name"]
        
        # If no explicit current phase, find first incomplete phase
        for phase in phases:
            if phase.get("status") == "pending":
                return phase["name"]
        
        return None
    
    
    def _extract_deliverables(self, phases: List[Dict[str, Any]]) -> List[str]:
        """Extract deliverables from phases.
        
        Args:
            phases: List of phase dictionaries
            
        Returns:
            List of deliverable names
        """
        deliverables = []
        for phase in phases:
            if phase.get("status") == "completed":
                deliverables.append(phase.get("name", ""))
        return deliverables
