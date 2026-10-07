from typing import Literal
from pydantic import BaseModel, Field

class Incident(BaseModel):
    incident_id: str
    location: str = Field(min_length=2)
    description: str = Field(min_length=5)
    rainfall_mm: float = Field(ge=0)
    road_status: Literal["open", "closed", "flooded", "unknown"] = "unknown"

class EvidenceAssessment(BaseModel):
    weather_signal: Literal["low", "moderate", "high"]
    road_status: str
    evidence_complete: bool
    evidence_score: int = Field(ge=0, le=100)
    score_label: Literal["LOW", "MODERATE", "STRONG"]

class RiskAssessment(BaseModel):
    level: Literal["LOW", "MEDIUM", "HIGH"]
    rationale: str

class DecisionProposal(BaseModel):
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    recommendation: str
    evidence_score: int = Field(ge=0, le=100)

class CriticReview(BaseModel):
    status: Literal["PASS", "REVISE"]
    reason: str

class SafetyReview(BaseModel):
    status: Literal["APPROVED", "APPROVED_WITH_LIMITATIONS", "HUMAN_REVIEW_REQUIRED", "BLOCKED"]
    reason: str

class EvaluationResult(BaseModel):
    scenario_id: str
    expected_priority: Literal["LOW", "MEDIUM", "HIGH"]
    predicted_priority: Literal["LOW", "MEDIUM", "HIGH"]
    baseline_priority: Literal["LOW", "MEDIUM", "HIGH"]
    expected_escalation: bool
    predicted_escalation: bool
    evidence_traceability: float = Field(ge=0, le=1)
    decision_agreement: bool
    baseline_agreement: bool
    missed_escalation: bool
    unnecessary_escalation: bool
    review_time_ms: float = Field(ge=0)
    reproducible: bool
