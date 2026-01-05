"""
Pattern Manager Module

Manages the pattern library including loading, updating, adding, and archiving patterns.
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PatternManager:
    """Manages pattern library with CRUD operations and archiving."""
    
    def __init__(self, pattern_library_path: str = "patterns.json"):
        """Initialize the pattern manager.
        
        Args:
            pattern_library_path: Path to the pattern library JSON file
        
        Raises:
            ValueError: If path contains traversal attempts (..)
        """
        # Validate path to prevent path traversal
        # Check for .. components before resolution to catch traversal attempts
        # This prevents attacks like "../../etc/passwd" while allowing absolute paths
        # for legitimate use cases (e.g., /tmp in tests)
        if ".." in Path(pattern_library_path).parts:
            raise ValueError(f"Path traversal detected in: {pattern_library_path}")
        
        # Resolve to absolute path for consistent path handling
        resolved_path = Path(pattern_library_path).resolve()
        self.pattern_library_path = str(resolved_path)
        
        self.patterns: List[Dict[str, Any]] = []
        self.changelog: List[Dict[str, Any]] = []
        
        # Try to load existing patterns
        if os.path.exists(self.pattern_library_path):
            self.load_patterns()
        else:
            logger.debug(f"Pattern library not found at {self.pattern_library_path}, will create new")
    
    def load_patterns(self) -> None:
        """Load patterns from JSON file."""
        try:
            with open(self.pattern_library_path, 'r') as f:
                data = json.load(f)
                self.patterns = data.get("patterns", [])
                self.changelog = data.get("changelog", [])
            logger.debug(f"Loaded {len(self.patterns)} patterns from {self.pattern_library_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.debug(f"Failed to load patterns: {e}")
            self.patterns = []
            self.changelog = []
    
    def save_patterns(self) -> None:
        """Save patterns to JSON file."""
        try:
            data = {
                "patterns": self.patterns,
                "changelog": self.changelog,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.pattern_library_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.patterns)} patterns to {self.pattern_library_path}")
        except IOError as e:
            logger.debug(f"Failed to save patterns: {e}")
            raise
    
    def load_from_ai_patterns_md(self, md_path: str = "docs/AI_PATTERNS_GUIDE.md") -> None:
        """Load patterns from AI_PATTERNS_GUIDE.md file.
        
        Args:
            md_path: Path to the AI_PATTERNS_GUIDE.md file
        
        Raises:
            ValueError: If path contains traversal attempts (..)
        """
        # Validate path to prevent path traversal
        # Check for .. components before resolution to catch traversal attempts
        if ".." in Path(md_path).parts:
            raise ValueError(f"Path traversal detected in: {md_path}")
        
        # Resolve to absolute path
        resolved_path = Path(md_path).resolve()
        md_path = str(resolved_path)
        
        if not os.path.exists(md_path):
            logger.debug(f"AI_PATTERNS.md not found at {md_path}")
            return
        
        try:
            with open(md_path, 'r') as f:
                content = f.read()
            
            # Parse patterns from markdown
            patterns_parsed = self._parse_patterns_from_markdown(content)
            
            # Merge with existing patterns
            for parsed_pattern in patterns_parsed:
                existing = self._find_pattern_by_name(parsed_pattern["name"])
                if existing:
                    # Update existing pattern but preserve metrics
                    existing["description"] = parsed_pattern["description"]
                    existing["bad_example"] = parsed_pattern["bad_example"]
                    existing["good_example"] = parsed_pattern["good_example"]
                else:
                    # Add new pattern
                    self.patterns.append(parsed_pattern)
                    self._add_changelog_entry("added", parsed_pattern["name"])
            
            logger.debug(f"Loaded {len(patterns_parsed)} patterns from {md_path}")
        except IOError as e:
            logger.debug(f"Failed to load AI_PATTERNS.md: {e}")
    
    def _parse_patterns_from_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse patterns from markdown content.
        
        Note: This uses simple string parsing for compatibility and simplicity.
        For production use with complex markdown, consider using a proper
        markdown parser like 'markdown' or 'mistune'.
        
        Args:
            content: Markdown content
            
        Returns:
            List of parsed patterns
        """
        patterns = []
        
        # Pattern names mapping
        pattern_mappings = {
            "NumPy Types Converted Before JSON Serialization": "numpy_json_serialization",
            "Bounds Checking Before List Access": "bounds_checking",
            "Specific Exceptions, Not Bare Except": "specific_exceptions",
            "Logger.debug() Instead of Print()": "logger_debug",
            "Metadata-Based Categorization Over String Matching": "metadata_categorization",
            "Proper Temp File Handling": "temp_file_handling",
            "Large File Processing": "large_file_processing"
        }
        
        # Split by pattern sections (### headers)
        sections = re.split(r'\n### \d+\. ', content)
        
        for section in sections[1:]:  # Skip first split (before first pattern)
            lines = section.split('\n')
            if not lines:
                continue
            
            # Get pattern name from first line
            pattern_name = lines[0].strip()
            pattern_id = pattern_mappings.get(pattern_name, pattern_name.lower().replace(' ', '_'))
            
            # Extract bad and good examples
            bad_example = self._extract_code_block(section, "❌ Bad Pattern")
            good_example = self._extract_code_block(section, "✅ Good Pattern")
            
            # Extract description (problems section)
            description = self._extract_description(section)
            
            pattern = {
                "pattern_id": str(uuid.uuid4()),
                "name": pattern_id,
                "description": description,
                "bad_example": bad_example,
                "good_example": good_example,
                "test_coverage": "",
                "occurrence_frequency": 0,
                "last_occurrence": None,
                "severity": "medium",
                "effectiveness_score": 0.5
            }
            
            patterns.append(pattern)
        
        return patterns
    
    def _extract_code_block(self, section: str, marker: str) -> str:
        """Extract code block following a marker.
        
        Args:
            section: Section of markdown
            marker: Marker text before code block
            
        Returns:
            Code block content
        """
        # Find marker
        marker_idx = section.find(marker)
        if marker_idx == -1:
            return ""
        
        # Find code block after marker
        code_start = section.find("```python", marker_idx)
        if code_start == -1:
            return ""
        
        code_end = section.find("```", code_start + 9)
        if code_end == -1:
            return ""
        
        return section[code_start + 9:code_end].strip()
    
    def _extract_description(self, section: str) -> str:
        """Extract description from pattern section.
        
        Args:
            section: Section of markdown
            
        Returns:
            Description text
        """
        # Find "Problems:" or "**Problems:**" section
        problems_idx = section.find("**Problems:**")
        if problems_idx == -1:
            problems_idx = section.find("Problems:")
        
        if problems_idx == -1:
            return "No description available"
        
        # Extract lines after Problems until next section
        lines = section[problems_idx:].split('\n')[1:6]
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('-'):
                description_lines.append(line[1:].strip())
            elif line.startswith('**') or line.startswith('###'):
                break
        
        return ' '.join(description_lines) if description_lines else "No description available"
    
    def _find_pattern_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find pattern by name.
        
        Args:
            name: Pattern name
            
        Returns:
            Pattern dictionary or None
        """
        for pattern in self.patterns:
            if pattern["name"] == name:
                return pattern
        return None
    
    def update_frequencies(self, frequency_data: List[Dict[str, Any]]) -> None:
        """Update pattern occurrence frequencies.
        
        Args:
            frequency_data: List of patterns with counts from analyzer
        """
        for freq_item in frequency_data:
            pattern_name = freq_item.get("pattern")
            count = freq_item.get("count", 0)
            
            pattern = self._find_pattern_by_name(pattern_name)
            if pattern:
                old_freq = pattern.get("occurrence_frequency", 0)
                pattern["occurrence_frequency"] = old_freq + count
                pattern["last_occurrence"] = datetime.now().isoformat()
                
                self._add_changelog_entry("updated_frequency", pattern_name, {
                    "old_frequency": old_freq,
                    "new_frequency": pattern["occurrence_frequency"]
                })
            else:
                logger.debug(f"Pattern '{pattern_name}' not found in library")
        
        logger.debug(f"Updated frequencies for {len(frequency_data)} patterns")
    
    def add_new_patterns(self, new_patterns: List[Dict[str, Any]]) -> None:
        """Add new patterns to the library.
        
        Args:
            new_patterns: List of new patterns with details
        """
        for new_pattern in new_patterns:
            pattern_name = new_pattern.get("pattern")
            count = new_pattern.get("count", 1)
            details = new_pattern.get("details", [])
            
            # Check if already exists
            if self._find_pattern_by_name(pattern_name):
                logger.debug(f"Pattern '{pattern_name}' already exists, skipping")
                continue
            
            # Create pattern entry
            pattern = {
                "pattern_id": str(uuid.uuid4()),
                "name": pattern_name,
                "description": self._generate_description_from_details(details),
                "bad_example": self._extract_bad_example_from_details(details),
                "good_example": "",
                "test_coverage": "",
                "occurrence_frequency": count,
                "last_occurrence": datetime.now().isoformat(),
                "severity": self._infer_severity_from_details(details),
                "effectiveness_score": 0.5
            }
            
            self.patterns.append(pattern)
            self._add_changelog_entry("added", pattern_name)
            logger.debug(f"Added new pattern: {pattern_name}")
    
    def _generate_description_from_details(self, details: List[Dict[str, Any]]) -> str:
        """Generate description from pattern details.
        
        Args:
            details: List of detail entries
            
        Returns:
            Description string
        """
        if not details:
            return "Auto-detected pattern"
        
        # Use error messages or reasons
        descriptions = []
        for detail in details[:3]:  # Limit to first 3
            if detail.get("type") == "bug":
                descriptions.append(detail.get("error", ""))
            elif detail.get("type") == "test_failure":
                descriptions.append(detail.get("reason", ""))
        
        return " | ".join(filter(None, descriptions)) or "Auto-detected pattern"
    
    def _extract_bad_example_from_details(self, details: List[Dict[str, Any]]) -> str:
        """Extract bad code example from details.
        
        Args:
            details: List of detail entries
            
        Returns:
            Bad example code
        """
        for detail in details:
            if detail.get("type") == "bug" and detail.get("code"):
                return detail["code"]
        return ""
    
    def _infer_severity_from_details(self, details: List[Dict[str, Any]]) -> str:
        """Infer severity from pattern details.
        
        Args:
            details: List of detail entries
            
        Returns:
            Severity level string
        """
        for detail in details:
            if detail.get("severity"):
                return detail["severity"]
        
        # Default to medium
        return "medium"
    
    def archive_unused_patterns(self, days: int = 90) -> List[str]:
        """Archive patterns with zero occurrences for specified days.
        
        Args:
            days: Number of days of no occurrences to trigger archiving
            
        Returns:
            List of archived pattern names
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        archived = []
        
        remaining_patterns = []
        for pattern in self.patterns:
            last_occurrence = pattern.get("last_occurrence")
            
            # If never occurred or occurred long ago
            should_archive = False
            if last_occurrence is None:
                should_archive = True
            else:
                try:
                    last_date = datetime.fromisoformat(last_occurrence)
                    if last_date < cutoff_date:
                        should_archive = True
                except ValueError:
                    pass
            
            if should_archive:
                archived.append(pattern["name"])
                self._add_changelog_entry("archived", pattern["name"], {
                    "reason": f"No occurrences in {days} days"
                })
            else:
                remaining_patterns.append(pattern)
        
        self.patterns = remaining_patterns
        logger.debug(f"Archived {len(archived)} patterns")
        return archived
    
    def _add_changelog_entry(
        self,
        action: str,
        pattern_name: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add entry to changelog.
        
        Args:
            action: Action performed (added/updated/archived)
            pattern_name: Name of the pattern
            details: Optional additional details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "pattern": pattern_name,
            "details": details or {}
        }
        self.changelog.append(entry)
    
    def get_pattern_names(self) -> List[str]:
        """Get list of all pattern names.
        
        Returns:
            List of pattern names
        """
        return [p["name"] for p in self.patterns]
    
    def get_pattern_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get pattern by name.
        
        Args:
            name: Pattern name
            
        Returns:
            Pattern dictionary or None
        """
        return self._find_pattern_by_name(name)
    
    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """Get all patterns.
        
        Returns:
            List of all patterns
        """
        return self.patterns.copy()
    
    def get_changelog(self) -> List[Dict[str, Any]]:
        """Get changelog entries.

        Returns:
            List of changelog entries
        """
        return self.changelog.copy()

    def sync_to_markdown(self, md_path: str = "docs/AI_PATTERNS_GUIDE.md") -> None:
        """Sync patterns back to AI_PATTERNS_GUIDE.md file.

        This creates a bidirectional sync, updating the markdown file with
        current pattern data from patterns.json.

        Args:
            md_path: Path to the AI_PATTERNS_GUIDE.md file

        Raises:
            ValueError: If path contains traversal attempts (..)
        """
        # Validate path to prevent path traversal
        if ".." in Path(md_path).parts:
            raise ValueError(f"Path traversal detected in: {md_path}")

        # Resolve to absolute path
        resolved_path = Path(md_path).resolve()
        md_path = str(resolved_path)

        try:
            # Read existing content
            existing_content = ""
            if os.path.exists(md_path):
                with open(md_path, 'r') as f:
                    existing_content = f.read()

            # Generate pattern sections
            pattern_sections = self._generate_pattern_sections()

            # If file exists, try to preserve non-pattern content
            if existing_content:
                # Find the patterns section
                patterns_start = existing_content.find("## Core Patterns")
                if patterns_start != -1:
                    # Find the next major section (## heading)
                    patterns_end = existing_content.find("\n## ", patterns_start + 20)
                    if patterns_end == -1:
                        patterns_end = len(existing_content)

                    # Replace patterns section
                    new_content = (
                        existing_content[:patterns_start] +
                        "## Core Patterns\n\n" +
                        pattern_sections +
                        "\n" +
                        existing_content[patterns_end:]
                    )
                else:
                    # No patterns section found, append
                    new_content = existing_content + "\n\n## Core Patterns\n\n" + pattern_sections
            else:
                # Create new file
                new_content = self._generate_full_markdown(pattern_sections)

            # Write back to file
            with open(md_path, 'w') as f:
                f.write(new_content)

            logger.debug(f"Synced {len(self.patterns)} patterns to {md_path}")

            # Add changelog entry
            self._add_changelog_entry("synced_to_markdown", "all_patterns", {
                "file": md_path,
                "pattern_count": len(self.patterns)
            })

        except IOError as e:
            logger.debug(f"Failed to sync patterns to markdown: {e}")
            raise

    def _generate_pattern_sections(self) -> str:
        """Generate markdown sections for all patterns.

        Returns:
            Markdown string with all pattern sections
        """
        sections = []

        # Sort patterns by occurrence frequency (descending)
        sorted_patterns = sorted(
            self.patterns,
            key=lambda p: p.get("occurrence_frequency", 0),
            reverse=True
        )

        for idx, pattern in enumerate(sorted_patterns, 1):
            name = pattern.get("name", "unknown")
            description = pattern.get("description", "No description available")
            bad_example = pattern.get("bad_example", "")
            good_example = pattern.get("good_example", "")
            frequency = pattern.get("occurrence_frequency", 0)
            effectiveness = pattern.get("effectiveness_score", 0.5)

            # Format pattern name for display
            display_name = name.replace("_", " ").title()

            section = f"### {idx}. {display_name}\n\n"
            section += f"**Pattern:** `{name}`\n\n"
            section += f"**Metrics:** Frequency: {frequency} | Effectiveness: {effectiveness:.1%}\n\n"
            section += f"**Problems:**\n{description}\n\n"

            if bad_example:
                section += f"❌ Bad Pattern:\n```python\n{bad_example}\n```\n\n"

            if good_example:
                section += f"✅ Good Pattern:\n```python\n{good_example}\n```\n\n"

            sections.append(section)

        return "\n".join(sections)

    def _generate_full_markdown(self, pattern_sections: str) -> str:
        """Generate a complete markdown file.

        Args:
            pattern_sections: Generated pattern sections

        Returns:
            Complete markdown content
        """
        return f"""# AI Patterns

Auto-generated pattern library.
Last updated: {datetime.now().isoformat()}

## Core Patterns

{pattern_sections}

## Usage

This file is automatically synced from patterns.json.
To update patterns, use the metrics system:

```bash
python -m metrics.integrate analyze
```
"""
