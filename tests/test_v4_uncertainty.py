from resilientcity.graph import build_graph
from resilientcity.evaluation import evaluate_all

def run(incident):
    return build_graph().invoke({"incident":incident,"revision_count":0,"trace":[]})

def test_missing_evidence_not_forced_into_low_medium_high():
    r=run({"incident_id":"T1","location":"A","description":"Road evidence unavailable","rainfall_mm":70,"road_status":"unknown"})
    assert r["decision"]["priority"]=="INSUFFICIENT_EVIDENCE"
    assert r["safety"]["status"]=="HUMAN_REVIEW_REQUIRED"

def test_contradictory_evidence_is_unresolved():
    r=run({"incident_id":"T2","location":"B","description":"Sources disagree on road","rainfall_mm":35,"road_status":"unknown","road_reports":["open","flooded"]})
    assert r["evidence"]["state"]=="CONTRADICTORY"
    assert r["decision"]["priority"]=="UNRESOLVED"

def test_out_of_scope_is_blocked():
    r=run({"incident_id":"T3","location":"C","description":"Chemical spill report","rainfall_mm":0,"road_status":"open","out_of_scope":True})
    assert r["decision"]["priority"]=="OUT_OF_SCOPE"
    assert r["safety"]["status"]=="BLOCKED"

def test_overlapping_critical_context_escalates():
    r=run({"incident_id":"T4","location":"Hospital","description":"Hospital access may be affected","rainfall_mm":30,"road_status":"open","critical_infrastructure":True})
    assert r["evidence"]["state"]=="OVERLAPPING"
    assert r["decision"]["priority"]=="MEDIUM"
    assert r["safety"]["status"]=="HUMAN_REVIEW_REQUIRED"

def test_adversarial_suite_has_no_forced_classification():
    _,m=evaluate_all()
    assert m["scenarios"]==20
    assert m["forced_classification_rate"]==0
    assert m["insufficient_evidence_recognition"]==1
    assert m["contradiction_detection"]==1
