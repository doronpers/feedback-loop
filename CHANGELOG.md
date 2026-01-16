# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- **Added**

- 20 additional test cases to improve coverage
- Tests for edge cases in NumPy type conversion (nested lists, non-NumPy passthrough)
- Tests for DataProcessor configuration with missing keys
- Tests for error handling in temp file operations
- Tests for file processing IOError scenarios
- Tests for FastAPI audio patterns error cleanup paths
- Tests for NumPy list/dict conversion in audio results
- Tests for AudioUploadResponse and AudioProcessingError models
- Tests for empty file validation
- Tests for duplicate test failure tracking
- Tests for invalid JSON loading

- **Changed**

- Test count increased from 99 to 119 tests
- Coverage improved from 85% to 91% (excluding demo files and CLI)
- Updated README badges to reflect current test count and coverage
- Updated README test suite breakdown

- **Fixed**

- Improved test coverage for error handling paths
- Enhanced edge case testing for all core patterns

## [1.0.0] - 2026-01-04

- **Added**

- Core pattern library with 9 essential patterns:
  1. NumPy Type Conversion
  2. Bounds Checking
  3. Specific Exceptions
  4. Structured Logging
  5. Metadata-Based Logic
  6. Temp File Handling
  7. Large File Processing
  8. FastAPI Streaming Uploads
  9. NumPy NaN/Inf Handling

- Metrics System:
  - MetricsCollector for tracking bugs, test failures, code reviews
  - MetricsAnalyzer for pattern analysis and trends
  - PatternManager for pattern library management
  - PatternAwareGenerator for code generation

- Testing:
  - 38 tests for core patterns
  - 25 tests for FastAPI patterns
  - 36 tests for metrics system
  - Total: 99 tests with high coverage

- Examples:
  - good_patterns.py - Best practices to follow
  - bad_patterns.py - Antipatterns to avoid
  - fastapi_audio_patterns.py - Production-ready FastAPI patterns
  - fastapi_audio_example.py - Complete FastAPI application

- **Infrastructure**

- MIT License
- Python 3.8+ support
- pytest-based testing
- CLI interface for metrics system
