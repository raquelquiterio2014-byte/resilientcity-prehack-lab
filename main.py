from resilientcity.graph import build_graph
from resilientcity.models import Incident

def main() -> None:
    incident = Incident(
        incident_id="LAB-001",
        location="Central Avenue",
        description="Heavy rainfall and reported street flooding near an intersection.",
        rainfall_mm=72.0,
        road_status="unknown",
    )
    app = build_graph()
    result = app.invoke({"incident": incident.model_dump(), "revision_count": 0, "trace": []})

    print("\n=== ResilientCity AI — Pre-Hackathon Lab ===")
    print(result["final_report"])
    print("\nTrace:")
    for event in result["trace"]:
        print(f"- {event}")

if __name__ == "__main__":
    main()
