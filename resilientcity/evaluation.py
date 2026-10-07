import json
from pathlib import Path
from statistics import mean
from time import perf_counter
from .graph import build_graph
from .models import EvaluationResult, Incident

DEFAULT_SCENARIOS=Path(__file__).resolve().parent.parent/"evaluation"/"scenarios.json"

def manual_baseline(i):
    if i.out_of_scope: return "OUT_OF_SCOPE"
    if not i.location.strip() or i.rainfall_mm is None or i.source_unavailable or i.evidence_stale: return "INSUFFICIENT_EVIDENCE"
    reports=set(i.road_reports+([] if i.road_status=="unknown" else [i.road_status]))
    if len(reports-{"unknown"})>1: return "UNRESOLVED"
    if i.road_status=="unknown": return "INSUFFICIENT_EVIDENCE"
    if i.road_status in {"flooded","closed"}: return "HIGH"
    if i.critical_infrastructure: return "MEDIUM"
    if i.rainfall_mm>=50: return "MEDIUM"
    return "LOW"

def requires_human_review(s): return s in {"HUMAN_REVIEW_REQUIRED","BLOCKED"}
def load_scenarios(path=DEFAULT_SCENARIOS):
    with Path(path).open(encoding="utf-8") as f: return json.load(f)
def _run_once(app,i):
    t=perf_counter(); r=app.invoke({"incident":i.model_dump(),"revision_count":0,"trace":[]}); return r,(perf_counter()-t)*1000

def evaluate_scenario(s,reproducibility_runs=3):
    app=build_graph(); i=Incident.model_validate(s["incident"]); r,ms=_run_once(app,i)
    repeated=[_run_once(app,i)[0] for _ in range(max(reproducibility_runs-1,0))]
    p=r["decision"]["priority"]; esc=requires_human_review(r["safety"]["status"]); b=manual_baseline(i); exp=s["expected_priority"]; exesc=bool(s["expected_escalation"]); e=r["evidence"]; exstate=s["expected_evidence_state"]
    fields=("state","weather_signal","road_status","evidence_score","score_label","missing_fields","conflicts")
    trace=sum(k in e for k in fields)/len(fields)
    sig=(p,r["safety"]["status"],r["decision"]["recommendation"],e["state"])
    repro=all((x["decision"]["priority"],x["safety"]["status"],x["decision"]["recommendation"],x["evidence"]["state"])==sig for x in repeated)
    expects_insufficient=exp=="INSUFFICIENT_EVIDENCE"
    expects_conflict=exstate=="CONTRADICTORY"
    forced=(exstate in {"MISSING","CONTRADICTORY","OUT_OF_SCOPE"} and p in {"LOW","MEDIUM","HIGH"})
    return EvaluationResult(scenario_id=s["scenario_id"],expected_priority=exp,predicted_priority=p,baseline_priority=b,expected_escalation=exesc,predicted_escalation=esc,expected_evidence_state=exstate,predicted_evidence_state=e["state"],evidence_traceability=trace,decision_agreement=p==exp,baseline_agreement=b==exp,appropriate_escalation=esc==exesc,missed_escalation=exesc and not esc,unnecessary_escalation=not exesc and esc,insufficient_evidence_recognized=(not expects_insufficient or p=="INSUFFICIENT_EVIDENCE"),contradiction_detected=(not expects_conflict or e["state"]=="CONTRADICTORY"),forced_classification=forced,workflow_time_ms=ms,reproducible=repro)

def evaluate_all(path=DEFAULT_SCENARIOS):
    rs=[evaluate_scenario(s) for s in load_scenarios(path)]; n=len(rs)
    ratio=lambda attr: mean(bool(getattr(r,attr)) for r in rs) if n else 0.0
    missing=[r for r in rs if r.expected_priority=="INSUFFICIENT_EVIDENCE"]; conflicts=[r for r in rs if r.expected_evidence_state=="CONTRADICTORY"]
    metrics={"scenarios":n,"decision_agreement":ratio("decision_agreement"),"baseline_agreement":ratio("baseline_agreement"),"evidence_traceability":mean(r.evidence_traceability for r in rs) if n else 0.0,"appropriate_escalation":ratio("appropriate_escalation"),"missed_escalations":sum(r.missed_escalation for r in rs),"unnecessary_escalations":sum(r.unnecessary_escalation for r in rs),"insufficient_evidence_recognition":mean(r.insufficient_evidence_recognized for r in missing) if missing else 1.0,"contradiction_detection":mean(r.contradiction_detected for r in conflicts) if conflicts else 1.0,"forced_classification_rate":mean(r.forced_classification for r in rs) if n else 0.0,"avg_workflow_time_ms":mean(r.workflow_time_ms for r in rs) if n else 0.0,"reproducibility":ratio("reproducible")}
    return rs,metrics
