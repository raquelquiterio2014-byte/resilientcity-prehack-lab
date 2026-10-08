"""Contracts for partner-supplied historical/field cases.

Evidence available by the decision cutoff is strictly separated from the later
documented outcome to reduce hindsight leakage.
"""
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

SourceQuality = Literal["HIGH","MEDIUM","LOW","UNKNOWN"]
Freshness = Literal["CURRENT","AGING","STALE","UNKNOWN"]
Verification = Literal["VERIFIED","CORROBORATED","UNVERIFIED","CONTRADICTORY","UNKNOWN"]

class FieldEvidenceItem(BaseModel):
    evidence_id: str
    claim: str
    source_type: str
    source_id: str | None = None
    observed_at: datetime | None = None
    retrieved_at: datetime | None = None
    source_quality: SourceQuality = "UNKNOWN"
    freshness: Freshness = "UNKNOWN"
    verification: Verification = "UNKNOWN"
    location: str | None = None
    structured_data: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None

class FieldContext(BaseModel):
    """Optional contextual vulnerability observed/estimated before cutoff."""
    antecedent_dry_days: int | None = Field(default=None, ge=0)
    soil_saturation_pct: float | None = Field(default=None, ge=0, le=100)
    impervious_surface_pct: float | None = Field(default=None, ge=0, le=100)
    drainage_status: Literal["clear","partially_blocked","clogged","unknown"] | None = None
    terrain_slope_pct: float | None = Field(default=None, ge=0)
    land_use: str | None = None
    observed_at: datetime | None = None
    source_ids: list[str] = Field(default_factory=list)
    methodology_notes: list[str] = Field(default_factory=list)

class HistoricalOutcome(BaseModel):
    """Outcome known after cutoff. Evaluator-only data; never sent to LLM."""
    summary: str
    documented_at: datetime | None = None
    reference_ids: list[str] = Field(default_factory=list)
    independent_label: str | None = None
    reviewer_notes: str | None = None

class FieldCase(BaseModel):
    case_id: str
    title: str
    location: str
    event_time: datetime | None = None
    evidence_cutoff: datetime
    evidence: list[FieldEvidenceItem] = Field(default_factory=list)
    context: FieldContext = Field(default_factory=FieldContext)
    later_outcome: HistoricalOutcome | None = None
    partner_notes: str | None = None

    def evidence_available_at_cutoff(self) -> list[FieldEvidenceItem]:
        available=[]
        for item in self.evidence:
            timestamp=item.observed_at or item.retrieved_at
            if timestamp is None or timestamp <= self.evidence_cutoff:
                available.append(item)
        return available

    def llm_payload(self) -> dict[str, Any]:
        """Cutoff-safe payload for future Evidence/Critic LLM calls."""
        return {
            "case_id":self.case_id,
            "title":self.title,
            "location":self.location,
            "event_time":self.event_time.isoformat() if self.event_time else None,
            "evidence_cutoff":self.evidence_cutoff.isoformat(),
            "context": self.context.model_dump(mode="json")
                if self.context.observed_at is not None and self.context.observed_at <= self.evidence_cutoff
                else {"status":"NOT_VERIFIED_AT_CUTOFF"},
            "evidence":[item.model_dump(mode="json") for item in self.evidence_available_at_cutoff()],
        }
