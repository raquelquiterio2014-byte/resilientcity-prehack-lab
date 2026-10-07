from .models import Incident, EvidenceAssessment, RiskAssessment, DecisionProposal, CriticReview, SafetyReview

DRY_DAYS_EXPERIMENTAL_THRESHOLD = 15
SOIL_SATURATION_EXPERIMENTAL_THRESHOLD = 80.0
HIGH_IMPERVIOUS_EXPERIMENTAL_THRESHOLD = 80.0

def _trace(state, message):
    return [*state.get("trace", []), message]

def planner_agent(state):
    return {"trace": _trace(state, "Planner: incident accepted; evidence quality, contextual vulnerability, and risk analysis requested.")}

def _vulnerability_flags(i: Incident) -> list[str]:
    flags=[]
    if i.antecedent_dry_days is not None and i.antecedent_dry_days > DRY_DAYS_EXPERIMENTAL_THRESHOLD:
        flags.append("PROLONGED_DRY_PERIOD")
    if i.soil_saturation_pct is not None and i.soil_saturation_pct > SOIL_SATURATION_EXPERIMENTAL_THRESHOLD:
        flags.append("HIGH_SOIL_SATURATION")
    if i.impervious_surface_pct is not None and i.impervious_surface_pct >= HIGH_IMPERVIOUS_EXPERIMENTAL_THRESHOLD:
        flags.append("HIGH_IMPERVIOUS_SURFACE")
    if i.drainage_status in {"partially_blocked","clogged"}:
        flags.append("DRAINAGE_CONSTRAINT")
    return flags

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
    flags=_vulnerability_flags(i)
    contextual="HIGH" if (("PROLONGED_DRY_PERIOD" in flags or "HIGH_SOIL_SATURATION" in flags) and ("DRAINAGE_CONSTRAINT" in flags or "HIGH_IMPERVIOUS_SURFACE" in flags)) else "ELEVATED" if flags else "LOW"
    if i.out_of_scope: state_name="OUT_OF_SCOPE"
    elif conflicts: state_name="CONTRADICTORY"
    elif missing: state_name="MISSING"
    elif i.critical_infrastructure or contextual!="LOW": state_name="OVERLAPPING"
    else: state_name="COMPLETE"
    score=max(0,100-25*len(set(missing))-35*len(conflicts)-(20 if i.evidence_stale else 0))
    label="STRONG" if score>=80 else "MODERATE" if score>=55 else "LOW"
    review=contextual!="LOW"
    e=EvidenceAssessment(state=state_name,weather_signal=weather,road_status=i.road_status,conflicts=conflicts,missing_fields=sorted(set(missing)),evidence_score=score,score_label=label,evidence_complete=not missing and not conflicts and not i.out_of_scope,contextual_uncertainty=contextual,vulnerability_flags=flags,human_review_trigger=review)
    return {"evidence":e.model_dump(),"trace":_trace(state,f"Evidence/VIGIE: state={state_name}, score={score}/100, contextual_uncertainty={contextual}, vulnerability_flags={flags}, missing={e.missing_fields}, conflicts={conflicts}.")}

def risk_agent(state):
    i=Incident.model_validate(state["incident"]); e=EvidenceAssessment.model_validate(state["evidence"])
    if e.state=="OUT_OF_SCOPE": level,r="OUT_OF_SCOPE","Incident is outside the validated urban-flood scope."
    elif e.state=="CONTRADICTORY": level,r="UNRESOLVED","Material evidence conflicts prevent reliable risk classification."
    elif e.state=="MISSING": level,r="UNRESOLVED","Critical evidence is missing, unavailable, or stale."
    elif i.road_status in {"flooded","closed"}: level,r="HIGH","Flooded or closed road is strong operational-risk evidence."
    elif e.contextual_uncertainty=="HIGH": level,r="MEDIUM","Moderate/low rainfall cannot be treated as low operational concern because antecedent terrain/drainage vulnerability is elevated."
    elif i.critical_infrastructure or e.contextual_uncertainty=="ELEVATED": level,r="MEDIUM","Contextual vulnerability or critical infrastructure raises impact and requires cautious interpretation."
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
        rec={"HIGH":"Escalate for human review and verify affected roads, terrain/drainage context, and critical infrastructure before action.","MEDIUM":"Request targeted verification of contextual vulnerability and present the recommendation for human review when uncertainty or impact is sensitive.","LOW":"Continue monitoring and document evidence; no high-impact action is recommended."}[p]
    d=DecisionProposal(priority=p,recommendation=rec,evidence_score=e.evidence_score)
    return {"decision":d.model_dump(),"trace":_trace(state,f"Decision: priority={p}; forced classification avoided={p in {'INSUFFICIENT_EVIDENCE','UNRESOLVED','OUT_OF_SCOPE'}}.")}

def critic_agent(state):
    e=EvidenceAssessment.model_validate(state["evidence"]); n=state.get("revision_count",0)
    if e.state in {"MISSING","CONTRADICTORY"} and n<1: x=CriticReview(status="REVISE",reason="Evidence is missing or contradictory; one bounded re-check is required.")
    elif e.state in {"MISSING","CONTRADICTORY","OUT_OF_SCOPE"}: x=CriticReview(status="ESCALATE",reason="Uncertainty remains after bounded review; do not force classification.")
    elif e.contextual_uncertainty!="LOW": x=CriticReview(status="ESCALATE",reason="VIGIE detected contextual terrain/drainage vulnerability that makes a simple rainfall-based classification unsafe.")
    else: x=CriticReview(status="PASS",reason="Evidence limitations are explicit and the proposal may proceed to deterministic safety review.")
    return {"critic":x.model_dump(),"trace":_trace(state,f"Critic: {x.status} — {x.reason}")}

def revision_agent(state):
    n=state.get("revision_count",0)+1
    return {"revision_count":n,"trace":_trace(state,f"Revision: bounded cycle {n}; unresolved evidence is preserved when no new source exists.")}

def safety_agent(state):
    d=DecisionProposal.model_validate(state["decision"]); e=EvidenceAssessment.model_validate(state["evidence"])
    if d.priority=="OUT_OF_SCOPE": x=SafetyReview(status="BLOCKED",reason="Outside validated scope; no operational recommendation is authorized.")
    elif d.priority in {"INSUFFICIENT_EVIDENCE","UNRESOLVED","HIGH"} or e.state in {"MISSING","CONTRADICTORY","OVERLAPPING"} or e.human_review_trigger: x=SafetyReview(status="HUMAN_REVIEW_REQUIRED",reason="Uncertainty, conflict, contextual vulnerability, critical context, or high impact requires a person to decide.")
    elif d.priority=="LOW": x=SafetyReview(status="APPROVED",reason="Decision support may be shown; no autonomous action is authorized.")
    else: x=SafetyReview(status="APPROVED_WITH_LIMITATIONS",reason="Recommendation may be shown with limitations; no autonomous action is authorized.")
    return {"safety":x.model_dump(),"trace":_trace(state,f"Safety: {x.status}.")}

def reporter_agent(state):
    i=Incident.model_validate(state["incident"]); d=DecisionProposal.model_validate(state["decision"]); e=EvidenceAssessment.model_validate(state["evidence"]); s=SafetyReview.model_validate(state["safety"])
    report=(f"Incident {i.incident_id} — {i.location or '[location missing]'}\nDecision: {d.priority}\nEvidence state: {e.state}\nContextual uncertainty: {e.contextual_uncertainty}\nVulnerability flags: {', '.join(e.vulnerability_flags) or 'none'}\nRecommendation: {d.recommendation}\nEvidence strength: {e.score_label} ({e.evidence_score}/100)\nMissing: {', '.join(e.missing_fields) or 'none'}\nConflicts: {', '.join(e.conflicts) or 'none'}\nSafety: {s.status}\nLimitation: {s.reason}\n\nThresholds used for contextual flags are experimental guardrails, not calibrated flood probabilities.\nWorkflow validation ≠ real-world readiness.\nA good outcome is not always a classification.\nPrinciple: AI recommends. AI explains. Humans decide.")
    return {"final_report":report,"trace":_trace(state,"Reporter: explainable response generated; shadow-mode principle preserved.")}
