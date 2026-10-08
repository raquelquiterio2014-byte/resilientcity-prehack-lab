from resilientcity.gemini_gateway import GeminiGateway
from resilientcity.llm_agents import evidence_prompt
from resilientcity.llm_contracts import LLMEvidenceAssessment

def test_gateway_falls_back_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result=GeminiGateway().generate_structured("test", LLMEvidenceAssessment)
    assert result.value is None
    assert result.source=="deterministic_fallback"
    assert result.attempts==0

def test_evidence_prompt_forbids_invention():
    prompt=evidence_prompt(
        {"incident_id":"T1"},
        {"state":"OVERLAPPING","vulnerability_flags":["DRAINAGE_CONSTRAINT"]},
    )
    assert "Do not invent" in prompt
    assert "experimental guardrails" in prompt


class _FakeValue:
    pass

def test_llm_mode_is_optional_and_fallback_is_explicit(monkeypatch):
    """No key must never break the V5 workflow."""
    from resilientcity.graph import build_graph
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    app=build_graph()
    result=app.invoke({
        "incident":{
            "incident_id":"LLM-FALLBACK","location":"Test Road",
            "description":"Moderate rainfall with road confirmed open.",
            "rainfall_mm":30,"road_status":"open"
        },
        "reasoning_mode":"llm_assisted","revision_count":0,"trace":[],"llm_status":{}
    })
    assert result["llm_status"]["evidence"]=="deterministic_fallback"
    assert result["llm_status"]["critic"]=="deterministic_fallback"
    assert result["safety"]["status"] in {"APPROVED","APPROVED_WITH_LIMITATIONS","HUMAN_REVIEW_REQUIRED","BLOCKED"}
    assert any("Deterministic Fallback" in line for line in result["trace"])

def test_deterministic_mode_does_not_request_gemini():
    from resilientcity.graph import build_graph
    app=build_graph()
    result=app.invoke({
        "incident":{
            "incident_id":"DET","location":"Test Road",
            "description":"Light rainfall with road confirmed open.",
            "rainfall_mm":10,"road_status":"open"
        },
        "reasoning_mode":"deterministic","revision_count":0,"trace":[],"llm_status":{}
    })
    assert result["llm_status"]["evidence"]=="not_requested"
    assert result["llm_status"]["critic"]=="not_requested"
