from typing import List, Dict, Any


class MarkdownSummaryReporter:
    """
    Generates GitHub-flavored markdown executive reports of Chain-of-Thought audit evaluations.
    """

    def __init__(self, run_metadata: Dict[str, Any], evaluation_records: List[Dict[str, Any]]):
        self.metadata = run_metadata
        self.records = evaluation_records

    def render(self) -> str:
        total = len(self.records)
        coherent = sum(1 for r in self.records if r.get("is_coherent", False))
        rate = round((coherent / total * 100), 1) if total > 0 else 0.0

        md = []
        md.append(f"# CoT Audit Executive Summary: {self.metadata.get('model_id', 'Unknown')}\n")
        md.append(f"- **Evaluated Traces:** {total}")
        md.append(f"- **Logical Coherence Rate:** {rate}%")
        md.append(f"- **Benchmark Dataset:** {self.metadata.get('benchmark', 'ReasoningBench-500')}\n")
        md.append("| Trace ID | Steps | Fallacies Detected | Coherence |")
        md.append("|---|:---:|---|:---:|")

        for r in self.records:
            t_id = r.get("trace_id", "N/A")
            steps = r.get("step_count", 0)
            fallacies = ", ".join(r.get("fallacies", [])) or "None"
            status = "✅ PASS" if r.get("is_coherent") else "❌ FAIL"
            md.append(f"| `{t_id}` | {steps} | {fallacies} | {status} |")

        return "\n".join(md)
