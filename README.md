# ResilientCity AI — Pre-Hackathon Learning Lab

> **Important:** This repository is a disposable learning and experimentation environment created before the Open Agent Hackathon 2026 build window. It is **not** the competition implementation.

ResilientCity AI explores an explainable multi-agent approach to urban flood incident decision support.

## Learning objective

The lab tests how specialized components can share structured state, challenge a proposed decision, request revision, apply safety constraints, and produce a human-readable result.

**AI recommends. AI explains. Humans decide.**

## Current V6 workflow

```text
Incident
   |
Planner
   |
Evidence / VIGIE
   |
Gemini Evidence (optional)
   |
Risk / Impact
   |
Decision
   |
Deterministic Critic
   |
Gemini Critic (optional)
   |---- REVISE ----> Revision ----> Evidence
   |
Safety
   |
Human Gate
   |
Reporter
   |
Explainable response
```

V6 supports deterministic and LLM-assisted reasoning modes. Gemini 2.5 Flash assists the Evidence and Critic stages only. Structured LLM outputs are Pydantic-validated and the workflow uses deterministic fallback when the LLM is unavailable or cannot provide a valid result. Safety remains deterministic, and the Human Gate is explicit in the graph.

## What is implemented in V6

- Python package structure and Pydantic data contracts
- LangGraph multi-agent state graph
- Planner, Evidence/VIGIE, Risk/Impact, Decision, Critic, Safety, Human Gate and Reporter roles
- Gemini 2.5 Flash assistance for Evidence and Critic
- structured LLM outputs with validation
- bounded LLM retry and deterministic fallback
- conditional Critic revision loop
- deterministic Safety constraints and human-review escalation
- explicit Human Gate
- Evidence Strength score (rule-based, not a calibrated probability)
- contextual evidence: antecedent dry days, soil saturation, impervious surface, drainage, terrain slope and land use
- missing, contradictory, stale and out-of-scope evidence handling
- Agent Trace and shared-state inspection
- desktop Tkinter GUI
- labelled synthetic/adversarial scenario evaluation
- retrospective Shadow Mode backend for timestamped field cases and independent human baselines
- Pytest test suite

## Not implemented / not claimed

- live weather API integration
- live geospatial/road-status API integration
- MCP tools/server
- FastAPI service
- production database/persistence
- Streamlit UI
- sponsor-technology integration
- calibrated flood probabilities
- validated production or emergency-response readiness
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


## V5 Experimental — VIGIE, field cases, and LLM-ready evidence reasoning

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

### V5-B — Gemini-assisted reasoning
V5-B introduced Gemini 2.5 Flash assistance in Evidence and Critic/Evaluator through structured Pydantic output, bounded retry, deterministic fallback, provenance-aware findings, and trace disclosure. Safety remained deterministic.

Partner-supplied field cases can be consumed by this reasoning path using only evidence available at or before the case cutoff. Later outcomes remain evaluator-only to reduce hindsight leakage.

**Complete data does not necessarily mean sufficient decision evidence.**

**AI recommends. AI explains. Humans decide.**


## V6 Final Pre-Hackathon Research Prototype

V6 consolidates the V5-B dual reasoning modes with timestamp-safe physical/contextual field evidence and retrospective Human Baseline / Shadow Mode evaluation. Gemini 2.5 Flash assists Evidence and Critic only; structured outputs are Pydantic-validated, retry is bounded, fallback is deterministic, and Safety remains deterministic. Critic/LLM escalation is propagated conservatively to Safety, and an explicit Human Gate represents cases requiring human review or out-of-scope routing.

Physical/contextual inputs include antecedent dry days, soil saturation, impervious surface, drainage, terrain slope and land use. Partner-supplied field observations are evidence inputs, not calibrated probabilities or universal hydrological laws. Historical context must be timestamped at/before the evidence cutoff to enter retrospective reasoning; later outcomes remain evaluator-only.

The GUI preserves the complete selected scenario payload so hidden scenario attributes such as conflicting road reports, critical infrastructure, stale/unavailable evidence and out-of-scope status are not lost when an analysis is launched.

### Evaluation status and research roadmap

The repository includes controlled synthetic/adversarial evaluation and a retrospective Shadow Mode backend. These are architecture/evaluation experiments, not evidence of real-world operational validity. Additional V6 scenario validation is still required before the pre-hackathon architecture is considered frozen.

Three real French cases have been received and integrated as timestamped `FieldCase` fixtures under `evaluation/historical/france/`: Pas-de-Calais (Nov 2023), Gard/Hérault (Oct 2024), and Nancy (May 2012). Their status remains **real French cases received — structured retrospective validation pending**. They are not yet claimed as validated V6 results. Supplied expected behaviors are treated only as test hypotheses/evaluator notes, not as agent inputs or ground truth. Source attributions and event details still require primary-source verification before research conclusions are drawn. Post-hackathon research candidates also include independent human baselines, Abstention Precision, Forced Classification Rate, Appropriate/Missed/Unnecessary Escalation, cost-sensitive escalation thresholds, inter-rater agreement, evidence traceability, reproducibility, review time and human-review burden.

V6 is the final pre-hackathon research prototype. It is not an operational emergency-response system and not the competition implementation.

**AI recommends. AI explains. Humans decide.**
