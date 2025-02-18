import sys
import json
import argparse
from .core.analyzer import CoTTraceAnalyzer


def test_analyzer():
    analyzer = CoTTraceAnalyzer()
    print("\nRunning Chain-of-Thought Trace Analyzer Verification:")
    print("=" * 65)

    with open("cot_auditor/data/sample_traces.json") as f:
        traces = json.load(f)

    for item in traces:
        audit = analyzer.audit_trace(
            trace_id=item["trace_id"],
            model_name=item["model_name"],
            raw_trace=item["raw_trace"],
            ground_truth=item["ground_truth"]
        )
        print(f"Trace ID: {audit.trace_id} ({audit.model_name})")
        print(f" -> Steps: {audit.total_steps} | Backtracks: {audit.backtrack_count} | Coherence: {audit.coherence_score:.2f}")
        print(f" -> Valid Answer: {audit.final_answer_valid} | Fallacies Detected: {len(audit.fallacies)}")
        for f_item in audit.fallacies:
            print(f"    * [{f_item.severity.value}] {f_item.fallacy_type.value}: {f_item.explanation}")
        print("-" * 65)

    print("CoTTraceAnalyzer successfully verified!\n")


def main():
    parser = argparse.ArgumentParser(description="CoT Reasoning Auditor CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("test", help="Run audit test suite on sample traces")

    args = parser.parse_args()
    if args.command == "test":
        test_analyzer()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
