"""V6 retrospective shadow-mode evaluation (research-only, no live dispatch).

Human baseline is an INDEPENDENT reviewer record, not a deterministic heuristic.
The outcome is never passed to the decision-support graph.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Literal
import json

from pydantic import BaseModel, Field, model_validator
from .field_cases import FieldCase
from .graph import build_graph
from .models import Incident, Priority

class HumanBaseline(BaseModel):
    case_id: str
    reviewer_id: str
    evidence_cutoff: datetime
    priority: Priority
    escalate: bool
    evidence_ids: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    next_action: str
    rationale: str
    review_time_seconds: float = Field(ge=0)
    reviewed_at: datetime | None = None
    outcome_blinded: bool = True

class ShadowResult(BaseModel):
    case_id: str
    ai_priority: Priority
    human_priority: Priority
    ai_escalate: bool
    human_escalate: bool
    priority_agreement: bool
    escalation_agreement: bool
    ai_workflow_time_ms: float = Field(ge=0)
    human_review_time_seconds: float = Field(ge=0)
    evidence_ids_available: list[str]
    human_evidence_ids_valid: bool
    ai_trace: list
    ai_safety_status: str
    later_outcome_summary: str | None = None
    retrospective_note: str = "Disagreement is not automatically an AI error; later outcomes are evaluator-only."
    evaluation_status: Literal["COMPARISON_ONLY","OUTCOME_DOCUMENTED"] = "COMPARISON_ONLY"

def cutoff_snapshot(case: FieldCase) -> dict:
    """Reject evidence without reliable timestamps; avoid accidental future leakage."""
    evidence = []
    for item in case.evidence:
        if item.observed_at is None and item.retrieved_at is None:
            continue
        # Both timestamps must be at/before cutoff if present.
        if any(t > case.evidence_cutoff for t in (item.observed_at,item.retrieved_at) if t is not None):
            continue
        evidence.append(item)
    context=None
    if case.context.observed_at is not None and case.context.observed_at <= case.evidence_cutoff:
        context=case.context.model_dump(mode="json")
    return {"case_id":case.case_id,"location":case.location,"evidence_cutoff":case.evidence_cutoff.isoformat(),"evidence":[e.model_dump(mode="json") for e in evidence],"context":context,"context_status":"VERIFIED_AT_CUTOFF" if context else "NOT_VERIFIED_AT_CUTOFF"}

def incident_from_snapshot(case: FieldCase, snapshot: dict) -> Incident:
    """Conservative mapping: unknown inputs remain unknown, never guessed."""
    rain = None
    road = "unknown"
    reports = []
    for e in snapshot["evidence"]:
        data=e.get("structured_data") or {}
        if "rainfall_mm" in data:
            try:
                value=float(data["rainfall_mm"])
                if value>=0: rain=value
            except (ValueError,TypeError): pass
        status=data.get("road_status")
        if status in {"open","closed","flooded","unknown"}:
            reports.append(status)
    known=[s for s in reports if s!="unknown"]
    if known: road=known[0]
    return Incident(incident_id=case.case_id,location=case.location,
        description=case.title if len(case.title)>=5 else "Historical flood incident",
        rainfall_mm=rain,road_status=road,road_reports=reports,
        antecedent_dry_days=(snapshot.get("context") or {}).get("antecedent_dry_days"), soil_saturation_pct=(snapshot.get("context") or {}).get("soil_saturation_pct"), impervious_surface_pct=(snapshot.get("context") or {}).get("impervious_surface_pct"), drainage_status=(snapshot.get("context") or {}).get("drainage_status"), terrain_slope_pct=(snapshot.get("context") or {}).get("terrain_slope_pct"), land_use=(snapshot.get("context") or {}).get("land_use"))

def compare_case(case: FieldCase, human: HumanBaseline, app=None, reasoning_mode: str = "deterministic") -> ShadowResult:
    if case.case_id!=human.case_id or case.evidence_cutoff!=human.evidence_cutoff:
        raise ValueError("Human review case/cutoff does not match historical case")
    if not human.outcome_blinded:
        raise ValueError("Human baseline must be blinded to the later outcome")
    snap=cutoff_snapshot(case)
    ids={e["evidence_id"] for e in snap["evidence"]}
    if not set(human.evidence_ids).issubset(ids):
        raise ValueError("Human review cites evidence unavailable at cutoff")
    incident=incident_from_snapshot(case,snap)
    graph=app or build_graph()
    start=perf_counter()
    output=graph.invoke({"incident":incident.model_dump(),"field_payload":snap,"reasoning_mode":reasoning_mode,"llm_status":{},"revision_count":0,"trace":[]})
    elapsed=(perf_counter()-start)*1000
    decision=output["decision"]["priority"]
    safety=output["safety"]["status"]
    escalate=safety in {"HUMAN_REVIEW_REQUIRED","BLOCKED"}
    return ShadowResult(case_id=case.case_id,ai_priority=decision,
        human_priority=human.priority,ai_escalate=escalate,human_escalate=human.escalate,
        priority_agreement=decision==human.priority,escalation_agreement=escalate==human.escalate,
        ai_workflow_time_ms=elapsed,human_review_time_seconds=human.review_time_seconds,
        evidence_ids_available=sorted(ids),human_evidence_ids_valid=True,
        ai_trace=output.get("trace",[]),ai_safety_status=safety,
        later_outcome_summary=case.later_outcome.summary if case.later_outcome else None,
        evaluation_status="OUTCOME_DOCUMENTED" if case.later_outcome else "COMPARISON_ONLY")

def evaluate_pair(case_path: str | Path, human_path: str | Path) -> dict:
    case=FieldCase.model_validate_json(Path(case_path).read_text(encoding="utf-8"))
    human=HumanBaseline.model_validate_json(Path(human_path).read_text(encoding="utf-8"))
    return compare_case(case,human).model_dump(mode="json")

def aggregate(results: list[ShadowResult]) -> dict:
    n=len(results)
    return {"cases":n,
            "priority_agreement_rate":sum(r.priority_agreement for r in results)/n if n else None,
            "escalation_agreement_rate":sum(r.escalation_agreement for r in results)/n if n else None,
            "ai_human_review_rate":sum(r.ai_escalate for r in results)/n if n else None,
            "human_escalation_rate":sum(r.human_escalate for r in results)/n if n else None,
            "avg_ai_workflow_ms":sum(r.ai_workflow_time_ms for r in results)/n if n else None,
            "avg_human_review_seconds":sum(r.human_review_time_seconds for r in results)/n if n else None,
            "note":"Agreement is descriptive; missed/unnecessary escalations require independent adjudication."}
