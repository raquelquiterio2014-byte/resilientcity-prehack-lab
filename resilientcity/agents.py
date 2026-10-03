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
    confidence = 0.90 if complete else 0.62
    evidence = EvidenceAssessment(
        weather_signal=weather_signal,
        road_status=incident.road_status,
        evidence_complete=complete,
        confidence=confidence,
    )
    return {"evidence": evidence.model_dump(), "trace": _trace(state, f"Evidence: weather={weather_signal}, road={incident.road_status}.")}

def risk_agent(state: ResilientCityState) -> dict:
    evidence = EvidenceAssessment.model_validate(state["evidence"])
    if evidence.weather_signal == "high" and evidence.road_status in {"flooded", "closed"}:
        level = "HIGH"
    elif evidence.weather_signal == "high":
        level = "MEDIUM"
    else:
        level = "LOW"
    risk = RiskAssessment(level=level, rationale="Deterministic lab assessment from rainfall and road evidence.")
    return {"risk": risk.model_dump(), "trace": _trace(state, f"Risk: {level}.")}

def decision_agent(state: ResilientCityState) -> dict:
    risk = RiskAssessment.model_validate(state["risk"])
    evidence = EvidenceAssessment.model_validate(state["evidence"])
    priority = risk.level
    recommendation = "Escalate for human review and verify road conditions before operational action."
    confidence = min(evidence.confidence, 0.85)
    decision = DecisionProposal(priority=priority, recommendation=recommendation, confidence=confidence)
    return {"decision": decision.model_dump(), "trace": _trace(state, f"Decision: priority={priority}, confidence={confidence:.2f}.")}

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
    return {"revision_count": count, "trace": _trace(state, f"Revision: cycle {count}; unresolved evidence remains explicit.")}

def safety_agent(state: ResilientCityState) -> dict:
    decision = DecisionProposal.model_validate(state["decision"])
    evidence = EvidenceAssessment.model_validate(state["evidence"])
    if not evidence.evidence_complete or decision.confidence < 0.70:
        review = SafetyReview(status="HUMAN_REVIEW_REQUIRED", reason="Critical evidence is incomplete or confidence is below threshold.")
    else:
        review = SafetyReview(status="APPROVED_WITH_LIMITATIONS", reason="Recommendation may be presented to a human operator; no autonomous action.")
    return {"safety": review.model_dump(), "trace": _trace(state, f"Safety: {review.status}.")}

def reporter_agent(state: ResilientCityState) -> dict:
    incident = Incident.model_validate(state["incident"])
    decision = DecisionProposal.model_validate(state["decision"])
    safety = SafetyReview.model_validate(state["safety"])
    report = (
        f"Incident {incident.incident_id} — {incident.location}\n"
        f"Priority: {decision.priority}\n"
        f"Recommendation: {decision.recommendation}\n"
        f"Confidence: {decision.confidence:.2f}\n"
        f"Safety status: {safety.status}\n"
        f"Limitation: {safety.reason}\n"
        "Principle: AI recommends. AI explains. Humans decide."
    )
    return {"final_report": report, "trace": _trace(state, "Reporter: explainable response generated.")}
