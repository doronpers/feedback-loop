#!/usr/bin/env python3
"""
feedback-loop Unified Demo
Consolidated demonstration of all framework capabilities.
Usage:
  python demo.py patterns   - Show core AI development patterns
  python demo.py fastapi    - Show memory-safe FastAPI audio processing
  python demo.py workflow   - Show full metrics loop and code generation
  python demo.py review     - Show AI code review with debriefing
"""

import argparse
import asyncio
import io
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

# Configure elegant logging
logging.basicConfig(
    level=logging.INFO, format="\033[90m%(levelname)s:\033[0m %(message)s"
)
logger = logging.getLogger("demo")


def print_header(text):
    print(f"\n\033[95m{'='*60}\033[0m")
    print(f"\033[1m  {text.upper()}\033[0m")
    print(f"\033[95m{'='*60}\033[0m")


def print_step(text):
    print(f"\n\033[94m➤ {text}\033[0m")


async def run_patterns_demo():
    from examples.good_patterns import (DataProcessor,
                                        categorize_by_metadata_good,
                                        cleanup_temp_file_good,
                                        debug_processing_good,
                                        get_first_item_good, parse_config_good,
                                        process_data_good,
                                        process_large_file_good,
                                        write_temp_file_good)

    print_header("Core AI Patterns")

    print_step("NumPy Serialization Safety")
    data = np.array([1.5, 2.5, 3.5])
    result = process_data_good(data)
    print(f"  Input: {data} -> Output: {result} ✅")

    print_step("Bounds Checking & Edge Cases")
    print(f"  Empty list handle: {get_first_item_good([])} ✅")

    print_step("Specific Exception Handling")
    print(f"  Invalid JSON handle: {parse_config_good('{bad}')} ✅")

    print_step("Temp File Hygiene")
    path, _ = write_temp_file_good(b"data")
    print(f"  Created: {path}")
    cleanup_temp_file_good(path)
    print(f"  Cleaned: {not os.path.exists(path)} ✅")


async def run_fastapi_demo():
    from fastapi import UploadFile

    from examples.fastapi_audio_patterns import (process_audio_file_chunked,
                                                 safe_audio_upload_workflow,
                                                 stream_upload_to_disk)

    print_header("FastAPI Audio Workflow (800MB Safe)")

    print_step("Streaming Upload Simulation")
    content = b"audio" * 1000
    file = UploadFile(filename="demo.wav", file=io.BytesIO(content))
    temp_path, success = await stream_upload_to_disk(file)
    print(f"  Streamed to: {temp_path} ({success}) ✅")

    print_step("Chunked Processing Simulation")
    result = await process_audio_file_chunked(temp_path, chunk_size=1024)
    print(f"  Processed {result['chunks_processed']} chunks ✅")

    if os.path.exists(temp_path):
        os.unlink(temp_path)


async def run_workflow_demo():
    from metrics.analyzer import MetricsAnalyzer
    from metrics.code_generator import PatternAwareGenerator
    from metrics.collector import MetricsCollector
    from metrics.pattern_manager import PatternManager

    print_header("Full Metrics Feedback Loop")

    print_step("1. Metrics Collection")
    collector = MetricsCollector()
    collector.log_bug(
        pattern="numpy_json_serialization",
        error="TypeError",
        code='{"v": np.float64(1)}',
        file_path="src/api.py",
        line=42,
    )
    print(f"  Collected bug report for 'numpy_json_serialization' ✅")

    print_step("2. Pattern Analysis")
    analyzer = MetricsAnalyzer(collector.export_dict())
    high_freq = analyzer.get_high_frequency_patterns(threshold=0)
    print(f"  Identified {len(high_freq)} high-frequency items ✅")

    print_step("3. Pattern-Aware Generation")
    generator = PatternAwareGenerator([], "1.0.0")
    result = generator.generate(
        "Process NumPy array", metrics_context=analyzer.get_context()
    )
    print(f"  Generated code with pattern awareness ✅")
    print(f"\033[92m{result.code[:150]}...\033[0m")


async def run_review_demo():
    from metrics.code_reviewer import CodeReviewer, display_debrief

    print_header("AI Code Review with Debrief")

    reviewer = CodeReviewer()
    if not reviewer.llm_manager.is_any_available():
        print(
            "\033[91m  Error: No LLM API key found (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY)\033[0m"
        )
        return

    code = "def calc(a, b): return a / b"
    print_step(f"Reviewing Code: {code}")
    result = reviewer.review_code(code)
    print(f"  Review Provider: {result['provider']}")
    print(f"\033[92m{result['review'][:200]}...\033[0m")

    if "debrief" in result:
        display_debrief(result["debrief"])


def main():
    parser = argparse.ArgumentParser(description="feedback-loop Unified Demo")
    parser.add_argument(
        "mode",
        nargs="?",
        default="patterns",
        choices=["patterns", "fastapi", "workflow", "review"],
        help="Demo mode to run",
    )

    args = parser.parse_args()

    try:
        if args.mode == "patterns":
            asyncio.run(run_patterns_demo())
        elif args.mode == "fastapi":
            asyncio.run(run_fastapi_demo())
        elif args.mode == "workflow":
            asyncio.run(run_workflow_demo())
        elif args.mode == "review":
            asyncio.run(run_review_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo stopped.")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
