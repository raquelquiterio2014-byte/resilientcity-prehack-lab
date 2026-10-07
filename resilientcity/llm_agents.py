"""LLM-assisted Evidence and Critic helpers for V5.

Gemini interprets/challenges evidence; deterministic VIGIE and Safety remain
authoritative guardrails. Later historical outcomes must never enter prompts.
"""
import json
from .gemini_gateway import GeminiGateway
from .llm_contracts import LLMEvidenceAssessment, LLMCriticAssessment

def evidence_prompt(incident: dict, deterministic_evidence: dict, field_payload: dict | None = None) -> str:
    safe = {
        "incident": incident,
        "deterministic_vigie": deterministic_evidence,
        "field_case_cutoff_payload": field_payload,
    }
    return (
        "You are the Evidence reasoning component of ResilientCity AI V5. "
        "Analyze only the supplied evidence. Do not invent observations, probabilities, "
        "hydrological laws, source reliability, or missing facts. Treat VIGIE thresholds as "
        "experimental guardrails. Identify supporting evidence IDs, contradictions, missing "
        "information, and uncertainty. Recommend PROCEED, REVISE, or ESCALATE. "
        "A good outcome can be escalation or refusal to conclude.\n\nINPUT:\n"
        + json.dumps(safe, ensure_ascii=False, default=str)
    )

def critic_prompt(incident: dict, deterministic_evidence: dict, decision: dict, llm_evidence: dict | None) -> str:
    safe = {
        "incident": incident,
        "deterministic_vigie": deterministic_evidence,
        "decision_proposal": decision,
        "llm_evidence_assessment": llm_evidence,
    }
    return (
        "You are the Critic/Evaluator of ResilientCity AI V5. Challenge unsupported claims "
        "and simple rainfall-only reasoning. Do not create new evidence or probabilities. "
        "Return PASS only when the proposal is supported within the supplied evidence; "
        "otherwise REVISE or ESCALATE. Human review is preferred when material uncertainty "
        "cannot be resolved from the supplied data.\n\nINPUT:\n"
        + json.dumps(safe, ensure_ascii=False, default=str)
    )

def run_llm_evidence(incident: dict, deterministic_evidence: dict, field_payload: dict | None = None, gateway=None):
    gateway = gateway or GeminiGateway()
    return gateway.generate_structured(
        evidence_prompt(incident, deterministic_evidence, field_payload),
        LLMEvidenceAssessment,
    )

def run_llm_critic(incident: dict, deterministic_evidence: dict, decision: dict, llm_evidence: dict | None, gateway=None):
    gateway = gateway or GeminiGateway()
    return gateway.generate_structured(
        critic_prompt(incident, deterministic_evidence, decision, llm_evidence),
        LLMCriticAssessment,
    )
