"""Structured contracts for V6 LLM-assisted agents.

No provider is selected here. These models define the validated boundary
between an LLM and the deterministic multi-agent workflow.
"""

from typing import Literal
from pydantic import BaseModel, Field


class LLMEvidenceFinding(BaseModel):
    claim: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    uncertainty: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    explanation: str


class LLMEvidenceAssessment(BaseModel):
    findings: list[LLMEvidenceFinding] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    recommendation: Literal["PROCEED", "REVISE", "ESCALATE"]


class LLMCriticAssessment(BaseModel):
    status: Literal["PASS", "REVISE", "ESCALATE"]
    challenged_claims: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    requested_evidence: list[str] = Field(default_factory=list)
    rationale: str
