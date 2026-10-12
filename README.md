# ResilientCity AI — Pre-Hackathon Learning & Research Lab

> **Important:** This repository documents the evolution of a disposable learning and experimentation environment created before the Open Agent Hackathon 2026 build window. It is **not** the competition implementation and should not be treated as an operational emergency-response system.

ResilientCity AI explores an explainable, human-centered **multi-agent system for urban flood incident decision support**. The project evolved through multiple preserved branches, from a deterministic orchestration baseline to a V6 research prototype with contextual evidence, Gemini 2.5 Flash assistance, deterministic safety, an explicit Human Gate, and retrospective-evaluation foundations.

**AI recommends. AI explains. Humans decide.**

## Repository purpose

This repository is intentionally versioned as a pre-hackathon laboratory. Its branches preserve different stages of the architecture so that the evolution of the system can be inspected rather than overwritten.

| Branch | Research stage | Main focus |
| --- | --- | --- |
| `main` | Project index | Evolution and repository boundaries |
| `v3` | Visual deterministic baseline | GUI, synthetic scenarios, traces and supervised evaluation |
| `v4-experimental` | Uncertainty/adversarial baseline | Missing, contradictory and out-of-scope evidence; escalation |
| `v5-experimental` | Contextual evidence | VIGIE-style vulnerability/context inputs and field-case contracts |
| `v5b-gemini` | LLM-assisted reasoning | Gemini 2.5 Flash in Evidence and Critic with deterministic fallback |
| `v6-final` | Final pre-hackathon research prototype | Consolidated multi-agent architecture, Human Gate, contextual evidence and retrospective Shadow Mode foundations |

Earlier branches remain available as development history. The most advanced pre-hackathon research stage is **`v6-final`**.

## Architecture evolution

### V3 — Visual deterministic baseline

V3 introduced the desktop GUI and made the multi-agent workflow observable.

Implemented capabilities included:

- incident input form
- Planner, Evidence, Risk/Impact, Decision, Critic/Evaluator, Safety and Reporter roles
- LangGraph shared state
- conditional revision loop
- deterministic safety review
- human-review escalation
- explainable report
- Agent Trace
- shared-state inspection
- labelled synthetic flood scenarios
- supervised evaluation
- rule-based **Evidence Strength score (0–100)**

The Evidence Strength score represents deterministic evidence completeness/strength. It is **not a calibrated probability of correctness**.

### V4 — Uncertainty and adversarial evaluation

V4 deliberately made evaluation harder rather than optimizing only for successful classifications.

The controlled scenario set was expanded with adversarial and boundary conditions including:

- missing evidence
- contradictory evidence
- stale or unavailable evidence
- overlapping critical-infrastructure context
- missing location or rainfall
- threshold cases
- out-of-scope incidents

The decision space was expanded beyond LOW / MEDIUM / HIGH to include:

- `INSUFFICIENT_EVIDENCE`
- `UNRESOLVED`
- `OUT_OF_SCOPE`

The Critic gained PASS / REVISE / ESCALATE behavior, while Safety remained deterministic.

> **Workflow validation ≠ real-world readiness.**

A useful outcome is not always a classification. Recognizing insufficient, contradictory, or out-of-scope evidence and escalating appropriately is also part of successful system behavior.

### V5 / V5-A — Contextual evidence and VIGIE-style reasoning

V5 added contextual evidence intelligence so that apparently complete data would not automatically be interpreted as sufficient decision evidence.

Contextual inputs include:

- antecedent dry days
- soil saturation
- impervious surface
- drainage condition
- contextual uncertainty
- vulnerability flags
- field-case contracts with explicit evidence cutoffs

Experimental contextual thresholds are learning-lab guardrails, **not universal hydrological laws and not calibrated flood probabilities**.

A central research principle emerged from this stage:

> **Complete data does not necessarily mean sufficient decision evidence.**

### V5-B — Gemini 2.5 Flash integration

V5-B introduced two reasoning modes:

- **Deterministic**
- **LLM-Assisted (Gemini 2.5 Flash)**

Gemini 2.5 Flash assists only the **Evidence** and **Critic/Evaluator** stages. It does not control the deterministic Safety boundary.

LLM-assisted reasoning includes:

- structured outputs
- Pydantic validation
- bounded retry
- deterministic fallback
- provenance-aware findings
- trace disclosure of Gemini vs. deterministic fallback
- conservative interaction with deterministic Critic/Safety logic

If Gemini is unavailable, a key is missing, quota is exhausted, or a valid structured response cannot be produced, the workflow remains runnable through deterministic fallback.

The LLM can make review stricter, but it cannot weaken deterministic safety constraints.

## V6 Final — Pre-Hackathon Research Prototype

V6 consolidates the strongest parts of the previous stages and is the most advanced research prototype in this repository.

### Current V6 multi-agent workflow

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

The architecture is intentionally more than a linear prompt chain. It studies shared state, specialist reasoning, critique, revision, escalation, fallback, safety constraints and human oversight.

### V6 implemented capabilities

- Python package structure
- Pydantic contracts
- LangGraph multi-agent state graph
- Planner Agent
- Evidence / VIGIE Agent
- Risk / Impact Agent
- Decision Agent
- deterministic Critic
- Gemini-assisted Evidence reasoning
- Gemini-assisted Critic review
- bounded LLM retry
- deterministic fallback
- conditional revision loop
- deterministic Safety Agent
- explicit Human Gate
- Reporter Agent
- Agent Trace
- shared-state inspection
- Evidence Strength
- handling of missing, contradictory, stale and out-of-scope evidence
- desktop Tkinter GUI
- synthetic/adversarial scenario evaluation
- retrospective Shadow Mode backend
- Pytest test suite

### Physical and contextual evidence

V6 can represent:

- rainfall/incident observations
- antecedent dry days
- soil saturation
- impervious surface
- drainage condition
- terrain slope
- land use
- road conditions
- critical-infrastructure context
- evidence freshness and conflicts

These inputs are evidence for reasoning. Their presence does not by itself establish a calibrated flood probability.

### Critic, Safety and Human Gate

V6 separates three responsibilities:

**Critic / Evaluator** challenges unsupported reasoning and can request revision or escalation.

**Safety** applies deterministic constraints and remains authoritative even when Gemini participates in reasoning.

**Human Gate** explicitly represents cases in which the workflow should stop relying on automated reasoning alone and route the situation for human review, including unresolved uncertainty and out-of-scope conditions.

The design principle remains:

> **AI can retry and challenge its own reasoning, but it should know when to stop and ask a human.**

## Retrospective evaluation foundations

V6 contains a retrospective Shadow Mode backend designed around an evidence cutoff.

The intended research sequence is:

```text
Evidence available up to cutoff
        |
        +--> AI multi-agent assessment
        |
        +--> independent human baseline
        |
Later historical outcome
        |
        +--> evaluator-only comparison
```

Later outcomes should not be exposed to the agents during retrospective reasoning. This boundary is intended to reduce hindsight leakage.

### Historical flood material

Three French cases have been structured as preliminary timestamped `FieldCase` fixtures under `evaluation/historical/france/`:

- Pas-de-Calais — November 2023
- Gard/Hérault — October 2024
- Nancy — May 2012

Their status remains:

**real French cases received — structured retrospective validation pending**

They are not claimed as validated V6 results. Supplied expected behaviors are evaluator/test hypotheses rather than agent inputs or ground truth, and source-level verification is still required before research conclusions are drawn.

Additional international flood events have been recorded separately as research candidates. Candidate status does **not** mean that they are executable or validated field cases. Time-stamped pre-cutoff evidence, independent baselines and source-level verification are required before retrospective execution.

## Evaluation direction

Controlled evaluation has included or motivated measures such as:

- decision agreement
- evidence traceability
- appropriate escalation
- missed escalation
- unnecessary escalation
- contradiction detection
- insufficient-evidence recognition
- forced-classification rate
- workflow execution time
- reproducibility

Post-hackathon research can extend this with independent human baselines, Abstention Precision / Justified Abstention, cost-sensitive escalation calibration, inter-rater agreement, human-review burden and clearer separation of AI workflow time from human review time.

The goal is not merely to maximize agreement. It is to study whether the system can make evidence traceable, recognize uncertainty, escalate appropriately and make the human operator's next decision clearer.

## What V6 does not claim

V6 does **not** claim:

- operational emergency-response readiness
- calibrated flood probabilities
- autonomous road closure
- autonomous evacuation orders
- autonomous emergency-resource dispatch
- validated real-time road status
- production-grade persistence
- complete live weather/geospatial integration
- production MCP infrastructure
- sponsor-technology integration
- real-world field validation

## Safety boundary

This research prototype does not autonomously close roads, dispatch emergency resources, order evacuations, or issue authoritative emergency commands.

Incomplete, conflicting, unsupported or out-of-scope situations can be revised, escalated, blocked or routed to human review depending on the workflow state.

**AI recommends. AI explains. Humans decide.**

## Running a branch

Each historical branch should be treated as its own development stage. Check out the branch you want to inspect and follow that branch's README and requirements.

Example:

```bash
git checkout v6-final
python -m pip install -r requirements.txt
python gui.py
```

For Gemini-assisted mode, configure `GEMINI_API_KEY` locally. **Never commit API keys or credentials to the repository.**

## Repository boundary and Open Agent Hackathon 2026

This repository is the **pre-hackathon learning/research record**.

It is intentionally separate from any competition implementation created during the official build window. Pre-existing work must be treated according to the applicable hackathon rules and should not be presented as newly developed competition code.

A separate real-case research project is also planned so that historical flood research can evolve without changing the preserved V6 synthetic/adversarial pre-hackathon architecture.

---

### Current milestone

**V6 Final Pre-Hackathon Research Prototype**

Multi-agent reasoning + contextual evidence + Gemini 2.5 Flash assistance + deterministic safety + explicit Human Gate + explainable traces + retrospective-evaluation foundations.

**Research prototype — not an operational emergency-response system.**
