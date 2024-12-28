from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


class FallacyType(str, Enum):
    PREMISE_HALLUCINATION = "premise_hallucination"
    CALCULATION_ERROR = "calculation_error"
    CIRCULAR_REASONING = "circular_reasoning"
    PREMATURE_CONCLUSION = "premature_conclusion"
    CONSTRAINT_NEGLECT = "constraint_neglect"


class AuditSeverity(str, Enum):
    MINOR = "minor"          # Self-corrected in subsequent thought step
    MODERATE = "moderate"    # Caused unnecessary token overthinking
    FATAL = "fatal"          # Propagated to erroneous final output


@dataclass
class ReasoningStep:
    step_index: int
    content: str
    tokens: int = 0
    is_backtracking: bool = False


@dataclass
class DetectedFallacy:
    step_index: int
    fallacy_type: FallacyType
    severity: AuditSeverity
    text_snippet: str
    explanation: str


@dataclass
class TrajectoryAudit:
    trace_id: str
    model_name: str
    total_steps: int
    total_tokens: int
    backtrack_count: int
    fallacies: List[DetectedFallacy] = field(default_factory=list)
    coherence_score: float = 1.0  # 0.0 to 1.0
    final_answer_valid: bool = True
