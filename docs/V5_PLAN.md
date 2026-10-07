# ResilientCity AI — V5 Experimental Plan

V5 extends the validated V4 uncertainty baseline without rewriting it.

## Research question
Can a multi-agent decision-support system reason safely over incomplete, conflicting and messy field evidence without pretending to know more than the evidence supports?

## V5-A — VIGIE / Evidence Intelligence
Evidence becomes first-class data with provenance, source quality, freshness, verification/corroboration, conflict detection and explicit uncertainty.

## V5-B — LLM-assisted Evidence + Critic
The first LLM integration is limited to Evidence and Critic/Evaluator. LLM output must be structured, validated with Pydantic, retried on invalid output, and fall back deterministically. Safety remains deterministic.

## V5-C — Deterministic vs LLM-assisted comparison
Both modes remain available so evaluation can test whether the LLM improves uncertainty handling rather than merely adding complexity.

## V5-D — Partner Field Cases / Historical Shadow Mode
A methodology/field partner may contribute real historical flood cases and messy evidence packages. The code must accept these cases without changing the agent architecture.

Each field case should support:
- case/incident ID and location
- event time and evidence cutoff time
- evidence items available at the cutoff
- source/provenance metadata
- later documented outcome kept separate from model input
- independent review/label when available
- notes about missing, conflicting, stale, or uncertain information

The system must NEVER expose post-cutoff outcome evidence to the reasoning agents during retrospective evaluation. The later outcome is used only by the evaluator.

Field cases are evaluation inputs, not proof of operational readiness.

## V5-E — Optional quantitative flood-risk source
Only if a defensible model or authoritative quantitative source is available. The LLM explains structured risk outputs; it does not invent flood probabilities.

## Stretch goal — REMPART
Case memory / retrieval of similar historical incidents may be explored only after the core V5 workflow is stable.

## Core principles
- Workflow validation ≠ real-world readiness.
- A good outcome is not always a classification.
- AI recommends. AI explains. Humans decide.
