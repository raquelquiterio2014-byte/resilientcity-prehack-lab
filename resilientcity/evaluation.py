import json
from pathlib import Path
from statistics import mean
from time import perf_counter

from .graph import build_graph
from .models import EvaluationResult, Incident

DEFAULT_SCENARIOS = Path(__file__).resolve().parent.parent / "evaluation" / "scenarios.json"

def manual_baseline(incident: Incident) -> str:
    if incident.road_status in {"flooded", "closed"}:
        return "HIGH"
    if incident.rainfall_mm >= 50:
        return "MEDIUM"
    if incident.rainfall_mm >= 20 and incident.road_status == "unknown":
        return "MEDIUM"
    return "LOW"

def requires_human_review(status: str) -> bool:
    return status in {"HUMAN_REVIEW_REQUIRED", "BLOCKED"}

def load_scenarios(path: str | Path = DEFAULT_SCENARIOS) -> list[dict]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)

def _run_once(app, incident: Incident) -> tuple[dict, float]:
    start = perf_counter()
    result = app.invoke({"incident": incident.model_dump(), "revision_count": 0, "trace": []})
    elapsed_ms = (perf_counter() - start) * 1000
    return result, elapsed_ms

def evaluate_scenario(scenario: dict, reproducibility_runs: int = 3) -> EvaluationResult:
    app = build_graph()
    incident = Incident.model_validate(scenario["incident"])
    result, review_time_ms = _run_once(app, incident)
    repeated = [_run_once(app, incident)[0] for _ in range(max(reproducibility_runs - 1, 0))]

    predicted_priority = result["decision"]["priority"]
    predicted_escalation = requires_human_review(result["safety"]["status"])
    baseline_priority = manual_baseline(incident)
    expected_priority = scenario["expected_priority"]
    expected_escalation = bool(scenario["expected_escalation"])

    evidence = result.get("evidence", {})
    traceability_fields = ("weather_signal", "road_status", "evidence_score", "score_label")
    evidence_traceability = sum(field in evidence for field in traceability_fields) / len(traceability_fields)

    signature = (predicted_priority, result["safety"]["status"], result["decision"]["recommendation"])
    reproducible = all(
        (item["decision"]["priority"], item["safety"]["status"], item["decision"]["recommendation"]) == signature
        for item in repeated
    )

    return EvaluationResult(
        scenario_id=scenario["scenario_id"],
        expected_priority=expected_priority,
        predicted_priority=predicted_priority,
        baseline_priority=baseline_priority,
        expected_escalation=expected_escalation,
        predicted_escalation=predicted_escalation,
        evidence_traceability=evidence_traceability,
        decision_agreement=predicted_priority == expected_priority,
        baseline_agreement=baseline_priority == expected_priority,
        missed_escalation=expected_escalation and not predicted_escalation,
        unnecessary_escalation=not expected_escalation and predicted_escalation,
        review_time_ms=review_time_ms,
        reproducible=reproducible,
    )

def evaluate_all(path: str | Path = DEFAULT_SCENARIOS) -> tuple[list[EvaluationResult], dict]:
    results = [evaluate_scenario(scenario) for scenario in load_scenarios(path)]
    count = len(results)
    metrics = {
        "scenarios": count,
        "decision_agreement": mean(r.decision_agreement for r in results) if count else 0.0,
        "baseline_agreement": mean(r.baseline_agreement for r in results) if count else 0.0,
        "evidence_traceability": mean(r.evidence_traceability for r in results) if count else 0.0,
        "missed_escalations": sum(r.missed_escalation for r in results),
        "unnecessary_escalations": sum(r.unnecessary_escalation for r in results),
        "avg_review_time_ms": mean(r.review_time_ms for r in results) if count else 0.0,
        "reproducibility": mean(r.reproducible for r in results) if count else 0.0,
    }
    return results, metrics
