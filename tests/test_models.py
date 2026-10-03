import pytest
from pydantic import ValidationError
from resilientcity.models import Incident

def test_incident_accepts_valid_data():
    incident = Incident(
        incident_id="T-01",
        location="Test Avenue",
        description="Reported flooding after heavy rainfall.",
        rainfall_mm=60,
        road_status="unknown",
    )
    assert incident.rainfall_mm == 60

def test_incident_rejects_negative_rainfall():
    with pytest.raises(ValidationError):
        Incident(
            incident_id="T-02",
            location="Test Avenue",
            description="Invalid rainfall scenario.",
            rainfall_mm=-1,
        )
