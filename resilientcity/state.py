from typing import Any, TypedDict
class ResilientCityState(TypedDict, total=False):
    incident: dict[str, Any]
    evidence: dict[str, Any]
    risk: dict[str, Any]
    decision: dict[str, Any]
    critic: dict[str, Any]
    safety: dict[str, Any]
    revision_count: int
    trace: list[str]
    final_report: str
