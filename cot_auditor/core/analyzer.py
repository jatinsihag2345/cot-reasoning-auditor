import re
from typing import List, Tuple
from .models import (
    ReasoningStep,
    DetectedFallacy,
    TrajectoryAudit,
    FallacyType,
    AuditSeverity
)


class CoTTraceAnalyzer:
    """
    Analyzes Chain-of-Thought reasoning traces from frontier reasoning models (o1, DeepSeek-R1).
    Detects logical fallacies, circular loops, self-correction quality, and overthinking drift.
    """

    BACKTRACK_PATTERNS = [
        r"\bwait,\b",
        r"\bhold on,\b",
        r"\bactually,\b",
        r"\blet me re-evaluate\b",
        r"\bthat's not right\b",
        r"\bthat cannot be correct\b",
        r"\blet me double-check\b"
    ]

    def parse_steps(self, raw_trace: str) -> List[ReasoningStep]:
        # Split by paragraphs or double newlines
        raw_blocks = [b.strip() for b in raw_trace.split("\n\n") if b.strip()]
        steps: List[ReasoningStep] = []
        for idx, block in enumerate(raw_blocks, 1):
            is_backtracking = any(re.search(pat, block, re.IGNORECASE) for pat in self.BACKTRACK_PATTERNS)
            tokens_approx = len(block.split()) * 4 // 3
            steps.append(ReasoningStep(step_index=idx, content=block, tokens=tokens_approx, is_backtracking=is_backtracking))
        return steps

    def audit_trace(self, trace_id: str, model_name: str, raw_trace: str, ground_truth: str) -> TrajectoryAudit:
        steps = self.parse_steps(raw_trace)
        fallacies: List[DetectedFallacy] = []
        backtrack_count = sum(1 for s in steps if s.is_backtracking)

        # 1. Circular reasoning loop detection
        seen_blocks = {}
        for s in steps:
            # Normalize step content
            norm = re.sub(r"\W+", " ", s.content.lower()).strip()
            if len(norm) > 40:
                if norm in seen_blocks:
                    seen_blocks[norm] += 1
                    if seen_blocks[norm] >= 2:
                        fallacies.append(DetectedFallacy(
                            step_index=s.step_index,
                            fallacy_type=FallacyType.CIRCULAR_REASONING,
                            severity=AuditSeverity.MODERATE,
                            text_snippet=s.content[:80] + "...",
                            explanation="Model repeated identical reasoning block without progressing toward solution."
                        ))
                else:
                    seen_blocks[norm] = 1

        # 2. Final answer validity check
        final_block = steps[-1].content.lower() if steps else ""
        final_answer_valid = ground_truth.lower() in final_block

        if not final_answer_valid:
            fallacies.append(DetectedFallacy(
                step_index=len(steps),
                fallacy_type=FallacyType.PREMATURE_CONCLUSION,
                severity=AuditSeverity.FATAL,
                text_snippet=final_block[:100],
                explanation=f"Final derived answer does not match ground truth '{ground_truth}'."
            ))

        total_tokens = sum(s.tokens for s in steps)

        # Score calculation: 1.0 base, penalized by detected fallacies
        penalty = sum(0.3 for f in fallacies if f.severity == AuditSeverity.FATAL) + \
                  sum(0.15 for f in fallacies if f.severity == AuditSeverity.MODERATE)
        coherence_score = max(0.0, round(1.0 - penalty, 2))

        return TrajectoryAudit(
            trace_id=trace_id,
            model_name=model_name,
            total_steps=len(steps),
            total_tokens=total_tokens,
            backtrack_count=backtrack_count,
            fallacies=fallacies,
            coherence_score=coherence_score,
            final_answer_valid=final_answer_valid
        )
