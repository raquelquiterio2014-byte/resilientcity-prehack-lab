from .models import Incident, EvidenceAssessment, RiskAssessment, DecisionProposal, CriticReview, SafetyReview
from .state import ResilientCityState

def _trace(state, message): return [*state.get("trace", []), message]

def planner_agent(state):
    return {"trace": _trace(state, "Planner: incident accepted; evidence quality and risk analysis requested.")}

def evidence_agent(state):
    i=Incident.model_validate(state["incident"]); missing=[]; conflicts=[]
    if not i.location.strip(): missing.append("location")
    if i.rainfall_mm is None: missing.append("rainfall")
    if i.road_status=="unknown": missing.append("road_status")
    reports=set(i.road_reports + ([] if i.road_status=="unknown" else [i.road_status]))
    if len(reports-{"unknown"})>1: conflicts.append("road_status")
    if i.source_unavailable: missing.append("source_unavailable")
    if i.evidence_stale: missing.append("fresh_evidence")
    weather="missing" if i.rainfall_mm is None else "high" if i.rainfall_mm>=50 else "moderate" if i.rainfall_mm>=20 else "low"
    if i.out_of_scope: state_name="OUT_OF_SCOPE"
    elif conflicts: state_name="CONTRADICTORY"
    elif missing: state_name="MISSING"
    elif i.critical_infrastructure: state_name="OVERLAPPING"
    else: state_name="COMPLETE"
    score=max(0,100-25*len(set(missing))-35*len(conflicts)-(20 if i.evidence_stale else 0))
    label="STRONG" if score>=80 else "MODERATE" if score>=55 else "LOW"
    e=EvidenceAssessment(state=state_name,weather_signal=weather,road_status=i.road_status,conflicts=conflicts,missing_fields=sorted(set(missing)),evidence_score=score,score_label=label,evidence_complete=state_name=="COMPLETE")
    return {"evidence":e.model_dump(),"trace":_trace(state,f"Evidence: state={state_name}, missing={e.missing_fields}, conflicts={conflicts}, score={score}/100.")}

def risk_agent(state):
    i=Incident.model_validate(state["incident"]); e=EvidenceAssessment.model_validate(state["evidence"])
    if e.state=="OUT_OF_SCOPE": level,r="OUT_OF_SCOPE","Incident is outside the validated urban-flood scope."
    elif e.state=="CONTRADICTORY": level,r="UNRESOLVED","Material evidence conflicts prevent reliable risk classification."
    elif e.state=="MISSING": level,r="UNRESOLVED","Critical evidence is missing, unavailable, or stale."
    elif i.road_status in {"flooded","closed"}: level,r="HIGH","Flooded or closed road is strong operational-risk evidence."
    elif i.critical_infrastructure: level,r="MEDIUM","Critical-infrastructure context raises impact despite an otherwise lower category."
    elif e.weather_signal=="high": level,r="MEDIUM","Heavy rainfall warrants increased monitoring even with an open road."
    else: level,r="LOW","Available supported indicators suggest lower immediate risk."
    x=RiskAssessment(level=level,rationale=r)
    return {"risk":x.model_dump(),"trace":_trace(state,f"Risk: {level} — {r}")}

def decision_agent(state):
    e=EvidenceAssessment.model_validate(state["evidence"]); r=RiskAssessment.model_validate(state["risk"])
    if e.state=="OUT_OF_SCOPE": p,rec="OUT_OF_SCOPE","Route to a human or a workflow validated for this incident type."
    elif e.state=="CONTRADICTORY": p,rec="UNRESOLVED","Do not force a category; reconcile conflicting evidence and require human review."
    elif e.state=="MISSING": p,rec="INSUFFICIENT_EVIDENCE","Obtain missing or fresh evidence before assigning LOW, MEDIUM, or HIGH."
    else:
        p=r.level
        rec={"HIGH":"Escalate for human review and verify affected roads/critical infrastructure before action.","MEDIUM":"Request targeted verification and present the recommendation for human review when impact is sensitive.","LOW":"Continue monitoring and document evidence; no high-impact action is recommended."}[p]
    d=DecisionProposal(priority=p,recommendation=rec,evidence_score=e.evidence_score)
    return {"decision":d.model_dump(),"trace":_trace(state,f"Decision: priority={p}; forced classification avoided={p in {'INSUFFICIENT_EVIDENCE','UNRESOLVED','OUT_OF_SCOPE'}}.")}

def critic_agent(state):
    e=EvidenceAssessment.model_validate(state["evidence"]); n=state.get("revision_count",0)
    if e.state in {"MISSING","CONTRADICTORY"} and n<1: x=CriticReview(status="REVISE",reason="Evidence is missing or contradictory; one bounded re-check is required.")
    elif e.state in {"MISSING","CONTRADICTORY","OUT_OF_SCOPE"}: x=CriticReview(status="ESCALATE",reason="Uncertainty remains after bounded review; do not force classification.")
    else: x=CriticReview(status="PASS",reason="Evidence limitations are explicit and the proposal may proceed to deterministic safety review.")
    return {"critic":x.model_dump(),"trace":_trace(state,f"Critic: {x.status} — {x.reason}")}

def revision_agent(state):
    n=state.get("revision_count",0)+1
    return {"revision_count":n,"trace":_trace(state,f"Revision: bounded cycle {n}; deterministic lab preserves unresolved evidence when no new source exists.")}

def safety_agent(state):
    d=DecisionProposal.model_validate(state["decision"]); e=EvidenceAssessment.model_validate(state["evidence"])
    if d.priority=="OUT_OF_SCOPE": x=SafetyReview(status="BLOCKED",reason="Outside validated scope; no operational recommendation is authorized.")
    elif d.priority in {"INSUFFICIENT_EVIDENCE","UNRESOLVED","HIGH"} or e.state in {"MISSING","CONTRADICTORY","OVERLAPPING"}: x=SafetyReview(status="HUMAN_REVIEW_REQUIRED",reason="Uncertainty, conflict, critical context, or high impact requires a person to decide.")
    elif d.priority=="LOW": x=SafetyReview(status="APPROVED",reason="Decision support may be shown; no autonomous action is authorized.")
    else: x=SafetyReview(status="APPROVED_WITH_LIMITATIONS",reason="Recommendation may be shown with limitations; no autonomous action is authorized.")
    return {"safety":x.model_dump(),"trace":_trace(state,f"Safety: {x.status}.")}

def reporter_agent(state):
    i=Incident.model_validate(state["incident"]); d=DecisionProposal.model_validate(state["decision"]); e=EvidenceAssessment.model_validate(state["evidence"]); s=SafetyReview.model_validate(state["safety"])
    report=(f"Incident {i.incident_id} — {i.location or '[location missing]'}\nDecision: {d.priority}\nEvidence state: {e.state}\nRecommendation: {d.recommendation}\nEvidence strength: {e.score_label} ({e.evidence_score}/100)\nMissing: {', '.join(e.missing_fields) or 'none'}\nConflicts: {', '.join(e.conflicts) or 'none'}\nSafety: {s.status}\nLimitation: {s.reason}\n\nWorkflow validation ≠ real-world readiness.\nA good outcome is not always a classification.\nPrinciple: AI recommends. AI explains. Humans decide.")
    return {"final_report":report,"trace":_trace(state,"Reporter: explainable response generated; shadow-mode principle preserved.")}
