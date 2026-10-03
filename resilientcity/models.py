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
    confidence: float = Field(ge=0, le=1)

class RiskAssessment(BaseModel):
    level: Literal["LOW", "MEDIUM", "HIGH"]
    rationale: str

class DecisionProposal(BaseModel):
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    recommendation: str
    confidence: float = Field(ge=0, le=1)

class CriticReview(BaseModel):
    status: Literal["PASS", "REVISE"]
    reason: str

class SafetyReview(BaseModel):
    status: Literal["APPROVED", "APPROVED_WITH_LIMITATIONS", "HUMAN_REVIEW_REQUIRED", "BLOCKED"]
    reason: str
