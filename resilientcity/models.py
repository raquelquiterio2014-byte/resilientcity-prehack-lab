from typing import Literal
from pydantic import BaseModel, Field

Priority = Literal["LOW","MEDIUM","HIGH","INSUFFICIENT_EVIDENCE","UNRESOLVED","OUT_OF_SCOPE"]
EvidenceState = Literal["COMPLETE","MISSING","CONTRADICTORY","OVERLAPPING","OUT_OF_SCOPE"]
ContextualUncertainty = Literal["LOW","ELEVATED","HIGH"]

class Incident(BaseModel):
    incident_id: str
    location: str = ""
    description: str = Field(min_length=5)
    rainfall_mm: float | None = Field(default=None, ge=0)
    road_status: Literal["open","closed","flooded","unknown"] = "unknown"
    road_reports: list[Literal["open","closed","flooded","unknown"]] = Field(default_factory=list)
    critical_infrastructure: bool = False
    out_of_scope: bool = False
    evidence_stale: bool = False
    source_unavailable: bool = False

    # V5 contextual vulnerability inputs. Thresholds are experimental guardrails,
    # not calibrated flood probabilities.
    antecedent_dry_days: int | None = Field(default=None, ge=0)
    soil_saturation_pct: float | None = Field(default=None, ge=0, le=100)
    impervious_surface_pct: float | None = Field(default=None, ge=0, le=100)
    drainage_status: Literal["clear","partially_blocked","clogged","unknown"] | None = None
    terrain_slope_pct: float | None = Field(default=None, ge=0)
    land_use: str | None = None

class EvidenceAssessment(BaseModel):
    state: EvidenceState
    weather_signal: Literal["missing","low","moderate","high"]
    road_status: str
    conflicts: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    evidence_score: int = Field(ge=0, le=100)
    score_label: Literal["LOW","MODERATE","STRONG"]
    evidence_complete: bool
    contextual_uncertainty: ContextualUncertainty = "LOW"
    vulnerability_flags: list[str] = Field(default_factory=list)
    human_review_trigger: bool = False

class RiskAssessment(BaseModel):
    level: Literal["LOW","MEDIUM","HIGH","UNRESOLVED","OUT_OF_SCOPE"]
    rationale: str

class DecisionProposal(BaseModel):
    priority: Priority
    recommendation: str
    evidence_score: int = Field(ge=0, le=100)

class CriticReview(BaseModel):
    status: Literal["PASS","REVISE","ESCALATE"]
    reason: str

class SafetyReview(BaseModel):
    status: Literal["APPROVED","APPROVED_WITH_LIMITATIONS","HUMAN_REVIEW_REQUIRED","BLOCKED"]
    reason: str

class EvaluationResult(BaseModel):
    scenario_id: str
    expected_priority: Priority
    predicted_priority: Priority
    baseline_priority: Priority
    expected_escalation: bool
    predicted_escalation: bool
    expected_evidence_state: EvidenceState
    predicted_evidence_state: EvidenceState
    evidence_traceability: float = Field(ge=0, le=1)
    decision_agreement: bool
    baseline_agreement: bool
    appropriate_escalation: bool
    missed_escalation: bool
    unnecessary_escalation: bool
    insufficient_evidence_recognized: bool
    contradiction_detected: bool
    forced_classification: bool
    workflow_time_ms: float = Field(ge=0)
    reproducible: bool
