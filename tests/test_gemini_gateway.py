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
