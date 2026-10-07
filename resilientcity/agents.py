from .models import (
    Incident, EvidenceAssessment, RiskAssessment, DecisionProposal,
    CriticReview, SafetyReview,
)
from .state import ResilientCityState

def _trace(state: ResilientCityState, message: str) -> list[str]:
    return [*state.get("trace", []), message]

def planner_agent(state: ResilientCityState) -> dict:
    return {"trace": _trace(state, "Planner: incident accepted; evidence and risk analysis requested.")}

def evidence_agent(state: ResilientCityState) -> dict:
    incident = Incident.model_validate(state["incident"])
    weather_signal = "high" if incident.rainfall_mm >= 50 else "moderate" if incident.rainfall_mm >= 20 else "low"
    complete = incident.road_status != "unknown"

    weather_points = 25 if weather_signal == "high" else 18 if weather_signal == "moderate" else 10
    road_points = 25 if incident.road_status in {"flooded", "closed"} else 20 if incident.road_status == "open" else 5
    completeness_points = 25 if complete else 10
    consistency_points = 20 if complete else 12
    evidence_score = min(weather_points + road_points + completeness_points + consistency_points, 100)
    score_label = "STRONG" if evidence_score >= 80 else "MODERATE" if evidence_score >= 55 else "LOW"

    evidence = EvidenceAssessment(
        weather_signal=weather_signal,
        road_status=incident.road_status,
        evidence_complete=complete,
        evidence_score=evidence_score,
        score_label=score_label,
    )
    return {
        "evidence": evidence.model_dump(),
        "trace": _trace(state, f"Evidence: weather={weather_signal}, road={incident.road_status}, score={evidence_score}/100 ({score_label})."),
    }

def risk_agent(state: ResilientCityState) -> dict:
    evidence = EvidenceAssessment.model_validate(state["evidence"])
    if evidence.road_status in {"flooded", "closed"}:
        level = "HIGH"
        rationale = "Flooded or closed road is treated as strong operational risk evidence."
    elif evidence.weather_signal == "high" and evidence.road_status == "unknown":
        level = "MEDIUM"
        rationale = "Heavy rainfall with unverified road condition requires caution."
    elif evidence.weather_signal == "high":
        level = "MEDIUM"
        rationale = "Heavy rainfall is present, but the road is reported open."
    elif evidence.weather_signal == "moderate" and evidence.road_status == "unknown":
        level = "MEDIUM"
        rationale = "Moderate rainfall plus missing road evidence creates uncertainty."
    else:
        level = "LOW"
        rationale = "Available deterministic indicators suggest lower immediate risk."
    risk = RiskAssessment(level=level, rationale=rationale)
    return {"risk": risk.model_dump(), "trace": _trace(state, f"Risk: {level} — {rationale}")}

def decision_agent(state: ResilientCityState) -> dict:
    risk = RiskAssessment.model_validate(state["risk"])
    evidence = EvidenceAssessment.model_validate(state["evidence"])
    priority = risk.level
    recommendations = {
        "HIGH": "Escalate immediately for human review; verify affected roads and critical infrastructure before operational action.",
        "MEDIUM": "Request targeted verification and prepare a human review of road and incident conditions.",
        "LOW": "Continue monitoring and document the available evidence; no high-impact action is recommended from current data.",
    }
    decision = DecisionProposal(
        priority=priority,
        recommendation=recommendations[priority],
        evidence_score=evidence.evidence_score,
    )
    return {
        "decision": decision.model_dump(),
        "trace": _trace(state, f"Decision: priority={priority}, evidence_score={evidence.evidence_score}/100."),
    }

def critic_agent(state: ResilientCityState) -> dict:
    evidence = EvidenceAssessment.model_validate(state["evidence"])
    revisions = state.get("revision_count", 0)
    if not evidence.evidence_complete and revisions < 1:
        review = CriticReview(status="REVISE", reason="Road condition is unverified; request another evidence cycle.")
    else:
        review = CriticReview(status="PASS", reason="Uncertainty is explicit and can proceed to safety review.")
    return {"critic": review.model_dump(), "trace": _trace(state, f"Critic: {review.status} — {review.reason}")}

def revision_agent(state: ResilientCityState) -> dict:
    count = state.get("revision_count", 0) + 1
    return {
        "revision_count": count,
        "trace": _trace(state, f"Revision: cycle {count}; no new source is available in the deterministic lab, so unresolved evidence is preserved for safety escalation."),
    }

def safety_agent(state: ResilientCityState) -> dict:
    decision = DecisionProposal.model_validate(state["decision"])
    evidence = EvidenceAssessment.model_validate(state["evidence"])
    if decision.priority == "HIGH":
        review = SafetyReview(status="HUMAN_REVIEW_REQUIRED", reason="High-priority recommendations require human operational review.")
    elif not evidence.evidence_complete or evidence.evidence_score < 70:
        review = SafetyReview(status="HUMAN_REVIEW_REQUIRED", reason="Critical evidence is incomplete or the rule-based evidence score is below the review threshold.")
    elif decision.priority == "LOW" and evidence.evidence_complete:
        review = SafetyReview(status="APPROVED", reason="Low-priority decision support may be presented without escalation; no autonomous action is authorized.")
    else:
        review = SafetyReview(status="APPROVED_WITH_LIMITATIONS", reason="Recommendation may be presented to a human operator; no autonomous action is authorized.")
    return {"safety": review.model_dump(), "trace": _trace(state, f"Safety: {review.status}.")}

def reporter_agent(state: ResilientCityState) -> dict:
    incident = Incident.model_validate(state["incident"])
    decision = DecisionProposal.model_validate(state["decision"])
    evidence = EvidenceAssessment.model_validate(state["evidence"])
    safety = SafetyReview.model_validate(state["safety"])
    report = (
        f"Incident {incident.incident_id} — {incident.location}\n"
        f"Priority: {decision.priority}\n"
        f"Recommendation: {decision.recommendation}\n"
        f"Evidence strength: {evidence.score_label} ({decision.evidence_score}/100)\n"
        "Score note: deterministic rule-based evidence score; NOT a calibrated probability of correctness.\n"
        f"Safety status: {safety.status}\n"
        f"Limitation: {safety.reason}\n"
        "Principle: AI recommends. AI explains. Humans decide."
    )
    return {"final_report": report, "trace": _trace(state, "Reporter: explainable response generated.")}
