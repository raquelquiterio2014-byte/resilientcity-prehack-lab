from typing import Any, TypedDict
class ResilientCityState(TypedDict, total=False):
    incident: dict[str, Any]
    evidence: dict[str, Any]
    field_payload: dict[str, Any]
    reasoning_mode: str
    llm_evidence: dict[str, Any]
    llm_critic: dict[str, Any]
    llm_status: dict[str, Any]
    risk: dict[str, Any]
    decision: dict[str, Any]
    critic: dict[str, Any]
    safety: dict[str, Any]
    revision_count: int
    trace: list[str]
    final_report: str
