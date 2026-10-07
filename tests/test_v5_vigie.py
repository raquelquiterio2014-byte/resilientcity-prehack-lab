from resilientcity.graph import build_graph
from resilientcity.models import Incident

def run(incident):
    return build_graph().invoke({"incident":incident.model_dump(),"revision_count":0,"trace":[]})

def test_dry_soil_and_drainage_context_prevents_simple_low_risk():
    result=run(Incident(
        incident_id="FIELD-GIROUSSENS-LAB",
        location="Giroussens",
        description="Moderate rainfall forecast with contextual terrain vulnerability.",
        rainfall_mm=25,
        road_status="open",
        antecedent_dry_days=16,
        impervious_surface_pct=85,
        drainage_status="clogged",
    ))
    assert result["evidence"]["contextual_uncertainty"]=="HIGH"
    assert "PROLONGED_DRY_PERIOD" in result["evidence"]["vulnerability_flags"]
    assert "DRAINAGE_CONSTRAINT" in result["evidence"]["vulnerability_flags"]
    assert result["risk"]["level"]=="MEDIUM"
    assert result["critic"]["status"]=="ESCALATE"
    assert result["safety"]["status"]=="HUMAN_REVIEW_REQUIRED"

def test_saturated_soil_triggers_contextual_review():
    result=run(Incident(
        incident_id="FIELD-SATURATION-LAB",
        location="Test Catchment",
        description="Low rainfall with high antecedent soil saturation.",
        rainfall_mm=18,
        road_status="open",
        soil_saturation_pct=95,
        drainage_status="partially_blocked",
    ))
    assert result["evidence"]["contextual_uncertainty"]=="HIGH"
    assert "HIGH_SOIL_SATURATION" in result["evidence"]["vulnerability_flags"]
    assert result["safety"]["status"]=="HUMAN_REVIEW_REQUIRED"

def test_complete_evidence_can_still_have_contextual_uncertainty():
    result=run(Incident(
        incident_id="CTX-001",
        location="Context Road",
        description="All primary fields exist but contextual vulnerability matters.",
        rainfall_mm=25,
        road_status="open",
        antecedent_dry_days=20,
    ))
    assert result["evidence"]["evidence_complete"] is True
    assert result["evidence"]["contextual_uncertainty"]=="ELEVATED"
    assert result["evidence"]["state"]=="OVERLAPPING"
    assert result["safety"]["status"]=="HUMAN_REVIEW_REQUIRED"
