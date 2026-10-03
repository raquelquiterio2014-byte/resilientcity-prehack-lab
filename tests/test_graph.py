from resilientcity.graph import build_graph
from resilientcity.models import Incident

def test_graph_requires_human_review_when_road_unknown():
    app = build_graph()
    incident = Incident(
        incident_id="T-03",
        location="Central Avenue",
        description="Heavy rain with unverified road condition.",
        rainfall_mm=70,
        road_status="unknown",
    )
    result = app.invoke({"incident": incident.model_dump(), "revision_count": 0, "trace": []})
    assert result["safety"]["status"] == "HUMAN_REVIEW_REQUIRED"
    assert result["revision_count"] == 1
    assert "Humans decide" in result["final_report"]
