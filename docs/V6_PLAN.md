# V6 Final Pre-Hackathon Research Prototype

V6 is the final pre-hackathon research prototype, not an operational emergency-response system or competition implementation.

## Research question
Can an explainable multi-agent system combine deterministic rules, LLM-assisted reasoning, physical/contextual evidence and independent human judgment to support urban-flood decisions under uncertainty without exceeding evidence or safety boundaries?

## Architecture
Incident → Planner → deterministic Evidence/VIGIE → optional Gemini Evidence → Risk/Impact → Decision → deterministic Critic → optional Gemini Critic → bounded Revision → deterministic Safety → Human Gate → Reporter.

Gemini 2.5 Flash uses Pydantic structured output, bounded retry and deterministic fallback. It may make critique stricter but cannot weaken deterministic Critic/Safety controls.

## Physical/contextual evidence
Antecedent dry days, soil saturation, impervious surface, drainage, terrain slope and land use are supported. Partner-supplied observations, including material contributed by Emmanuel Dorlet, are evidence inputs—not universal hydrological laws, calibrated probabilities, or automatically verified facts. Historical context enters retrospective reasoning only when timestamped at/before the evidence cutoff. Later outcomes are evaluator-only.

## Evaluation
Standard synthetic evaluation tests workflow behaviour. Historical Shadow Mode compares the AI with an independent outcome-blinded HumanBaseline using the same cutoff. Agreement is descriptive; missed/unnecessary escalation requires independent adjudication.

AI recommends. AI explains. Humans decide.
