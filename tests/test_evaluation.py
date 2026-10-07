from resilientcity.evaluation import evaluate_all, evaluate_scenario, manual_baseline
from resilientcity.models import Incident

def test_manual_baseline_treats_flooded_road_as_high():
    incident = Incident(
        incident_id="B-01", location="River Road",
        description="Flooded road after rainfall.", rainfall_mm=12, road_status="flooded"
    )
    assert manual_baseline(incident) == "HIGH"

def test_evaluation_recognizes_missing_evidence_and_human_review():
    scenario = {
        "scenario_id": "E-01",
        "incident": {
            "incident_id": "E-01", "location": "Central Avenue",
            "description": "Heavy rainfall and unknown road condition.",
            "rainfall_mm": 72, "road_status": "unknown"
        },
        "expected_priority": "INSUFFICIENT_EVIDENCE",
        "expected_escalation": True,
        "expected_evidence_state": "MISSING"
    }
    result = evaluate_scenario(scenario, reproducibility_runs=2)
    assert result.decision_agreement is True
    assert result.predicted_escalation is True
    assert result.insufficient_evidence_recognized is True
    assert result.forced_classification is False
    assert result.reproducible is True

def test_v4_evaluation_suite():
    _, metrics = evaluate_all()
    assert metrics["scenarios"] == 20
    assert metrics["missed_escalations"] == 0
    assert metrics["evidence_traceability"] == 1.0
    assert metrics["insufficient_evidence_recognition"] == 1.0
    assert metrics["contradiction_detection"] == 1.0
    assert metrics["forced_classification_rate"] == 0.0
