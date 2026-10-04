from dataclasses import dataclass
from typing import List


@dataclass
class ReasoningEfficiencyScore:
    productive_tokens: int
    overthinking_tokens: int
    efficiency_ratio: float
    is_excessive: bool


class OverthinkingScorer:
    """
    Quantifies overthinking penalties when reasoning models cycle through
    redundant self-corrections on already solved subproblems.
    """

    @staticmethod
    def calculate_efficiency(total_tokens: int, backtrack_tokens: int, max_expected_tokens: int = 2000) -> ReasoningEfficiencyScore:
        overthinking = max(0, backtrack_tokens - int(total_tokens * 0.25))
        productive = max(0, total_tokens - overthinking)
        ratio = round(productive / total_tokens, 2) if total_tokens > 0 else 1.0
        is_excessive = total_tokens > max_expected_tokens and ratio < 0.60

        return ReasoningEfficiencyScore(
            productive_tokens=productive,
            overthinking_tokens=overthinking,
            efficiency_ratio=ratio,
            is_excessive=is_excessive
        )
