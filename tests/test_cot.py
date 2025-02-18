from cot_auditor.core.analyzer import CoTTraceAnalyzer
from cot_auditor.core.models import FallacyType


def test_cot_backtrack_detection():
    analyzer = CoTTraceAnalyzer()
    trace = "Let's assume x = 5.\n\nWait, that's not right. If x = 5, then 2x = 10, not 12.\n\nLet's try x = 6."
    steps = analyzer.parse_steps(trace)
    assert len(steps) == 3
    assert steps[1].is_backtracking is True


def test_cot_circular_loop():
    analyzer = CoTTraceAnalyzer()
    trace = "Compute prime factorization of 91.\n\nLet's check if 91 is divisible by 3. Sum is 10 so no.\n\nLet's check if 91 is divisible by 3. Sum is 10 so no."
    audit = analyzer.audit_trace("t1", "mock", trace, "7, 13")
    assert any(f.fallacy_type == FallacyType.CIRCULAR_REASONING for f in audit.fallacies)
