from resilientcity.evaluation import evaluate_all, evaluate_scenario, manual_baseline
from resilientcity.models import Incident

def test_manual_baseline_treats_flooded_road_as_high():
    incident = Incident(
        incident_id="B-01", location="River Road",
        description="Flooded road after rainfall.", rainfall_mm=12, road_status="flooded"
    )
    assert manual_baseline(incident) == "HIGH"

def test_evaluation_detects_expected_human_review():
    scenario = {
        "scenario_id": "E-01",
        "incident": {
            "incident_id": "E-01", "location": "Central Avenue",
            "description": "Heavy rainfall and unknown road condition.",
            "rainfall_mm": 72, "road_status": "unknown"
        },
        "expected_priority": "MEDIUM",
        "expected_escalation": True
    }
    result = evaluate_scenario(scenario, reproducibility_runs=2)
    assert result.decision_agreement is True
    assert result.predicted_escalation is True
    assert result.missed_escalation is False
    assert result.reproducible is True

def test_evaluation_suite_has_no_missed_escalations():
    _, metrics = evaluate_all()
    assert metrics["scenarios"] >= 8
    assert metrics["missed_escalations"] == 0
    assert metrics["evidence_traceability"] == 1.0
