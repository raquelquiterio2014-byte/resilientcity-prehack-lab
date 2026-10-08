# ResilientCity AI — Pre-Hackathon Learning Lab

> **Important:** This repository is a disposable learning and experimentation environment created before the Open Agent Hackathon 2026 build window. It is **not** the competition implementation.

ResilientCity AI explores an explainable multi-agent approach to urban flood incident decision support.

## Learning objective

The lab tests how specialized components can share structured state, challenge a proposed decision, request revision, apply safety constraints, and produce a human-readable result.

**AI recommends. AI explains. Humans decide.**

## Current lab workflow

```text
Incident
   |
Planner
   |
Evidence
   |
Risk / Impact
   |
Decision
   |
Critic / Evaluator
   |---- REVISE ----> Revision ----> Evidence
   |
  PASS
   |
Safety
   |
Reporter
   |
Explainable response
```

The current implementation is deliberately deterministic. Agent names represent specialized workflow roles used to study multi-agent orchestration patterns; no external LLM is called yet.

## What is implemented

- Python package structure
- Pydantic data contracts
- LangGraph state graph
- Planner role
- Evidence role
- Risk / Impact role
- Decision role
- Critic / Evaluator role
- Conditional revision loop
- Safety review
- Human-review escalation
- Reporter role
- Execution trace
- Pytest tests
- Example incident

## Not implemented yet

- LLM integration
- live weather API
- geospatial API
- MCP tools/server
- FastAPI
- SQLite persistence
- Streamlit UI
- sponsor technologies
- production data
- autonomous emergency actions

## Requirements

Recommended: Python 3.12.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python main.py
```

Tests:

```bash
python -m pytest -q
```

## Safety boundary

This educational lab does not autonomously close roads, dispatch emergency resources, order evacuations, or issue authoritative emergency commands. Incomplete evidence and low-confidence situations are escalated for human review.

## Repository boundary

Any future hackathon competition implementation should be created separately during the official build window and should comply with the applicable official rules. Code from this learning repository should not be assumed to be eligible for reuse in a competition submission.


## V3 — Visual GUI

V3 adds a desktop graphical interface for the ResilientCity pre-hackathon learning lab.

- Incident input form
- Multi-agent analysis dashboard
- Priority and confidence indicators
- Safety / Human Gate status
- Explainable report
- Agent execution trace
- Shared LangGraph state
- Visual architecture panel
- Windows launcher (`run_gui.bat`)

Run:

```bash
python gui.py
```

Or on Windows, double-click `run_gui.bat`.

> V3 remains a pre-hackathon educational lab. It is not the competition implementation.


## Supervised Pilot Evaluation

V3 now includes an evaluation layer for labelled synthetic flood scenarios. It compares the multi-agent recommendation with an expected label and a simple deterministic manual baseline.

Current pilot metrics include:
- decision agreement
- baseline agreement
- evidence traceability
- missed escalations
- unnecessary escalations
- review time
- reproducibility

Run the evaluation suite through `resilientcity/evaluation.py` or `pytest`.

### Evidence score

The former percentage-style confidence display has been replaced by a deterministic **Evidence Strength score (0–100)**. It summarizes rule-based evidence completeness/strength and is explicitly **not a calibrated probability of correctness**.

The synthetic scenarios are stored in `evaluation/scenarios.json`. This is a supervised learning/evaluation lab, not a validated emergency-response benchmark or production pilot.


## V4 Experimental — Uncertainty, adversarial evaluation, and shadow-mode boundary

V4 preserves V3 as the controlled baseline and deliberately makes the evaluation less favorable to the system. The 8 original synthetic cases remain, and 12 adversarial/boundary cases add missing evidence, contradictory sources, overlapping critical-infrastructure context, threshold cases, stale/unavailable evidence, missing location/rainfall, and out-of-scope incidents.

The decision space is no longer forced to LOW / MEDIUM / HIGH. V4 can return:
- INSUFFICIENT_EVIDENCE
- UNRESOLVED
- OUT_OF_SCOPE

The Critic has PASS / REVISE / ESCALATE routes. Safety remains deterministic and can require human review or block an out-of-scope recommendation.

Evaluation now includes decision agreement, manual-baseline agreement, evidence traceability, appropriate escalation, missed/unnecessary escalation, insufficient-evidence recognition, contradiction detection, forced-classification rate, workflow time, and reproducibility.

> **Workflow validation ≠ real-world readiness.**

> **These controlled scenarios are being used to evaluate architecture behaviour, traceability, escalation and reproducibility.**

> **A good outcome is not always a classification. When evidence is missing, contradictory, or outside the system’s validated scope, recognising uncertainty and escalating to a human is itself a successful outcome.**

### Roadmap boundary

The next research stage is LLM-assisted Evidence and Critic roles using structured output, Pydantic validation, provenance, bounded retry, and deterministic fallback. The deterministic Safety role remains authoritative for the lab safety boundary.

Historical-case evaluation is intentionally not claimed here. Before any operational pilot, historical cases should be independently reviewed/labelled and compared with a manual baseline. Any operational pilot should begin in **shadow mode**, where the system logs recommendations but people make every operational decision.

**AI recommends. AI explains. Humans decide.**


## V5-B Gemini — VIGIE, field cases, and LLM-assisted evidence reasoning

V5 preserves V4 as the deterministic uncertainty baseline and adds contextual evidence intelligence.

### Implemented in V5-A
- VIGIE-style contextual vulnerability flags
- antecedent dry-period input
- soil-saturation input
- impervious-surface input
- drainage-condition input
- separation between evidence completeness and contextual uncertainty
- Human Gate escalation when apparently complete evidence still contains material terrain/drainage vulnerability
- partner field-case contracts with an explicit evidence cutoff
- strict separation of later historical outcome from future LLM input
- Giroussens challenge-case template, explicitly marked as partner-supplied and pending independent documentation
- regression tests for dry-period/drainage and saturated-soil conditions

The current contextual thresholds (>15 dry days, >80% soil saturation, >=80% impervious surface) are **experimental guardrails for the learning lab**, not universal hydrological laws and not calibrated flood probabilities.

### Implemented V5-B — dual reasoning modes
The GUI now exposes **Deterministic** and **LLM-Assisted (Gemini 2.5 Flash)** modes.

In LLM-Assisted mode, Gemini is called only for Evidence reasoning and Critic/Evaluator review. Outputs are structured and validated with Pydantic, calls use bounded retry, and failures (including missing key/quota/provider errors) are disclosed in Agent Trace as **Deterministic Fallback**. The deterministic Evidence/VIGIE, Risk/Decision rules and Safety Gate remain authoritative guardrails. Gemini may make Critic review stricter, but it cannot weaken deterministic Critic/Safety decisions.

Configure `GEMINI_API_KEY` in the environment to enable live calls. Without a key the workflow remains runnable through deterministic fallback.

This remains a pre-hackathon learning lab, not the competition implementation.

Partner-supplied field cases are designed to be consumed by this LLM path using only evidence available at or before the case cutoff. Later outcomes remain evaluator-only to reduce hindsight leakage.

**Complete data does not necessarily mean sufficient decision evidence.**

**AI recommends. AI explains. Humans decide.**
