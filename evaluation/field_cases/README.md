# Partner Field Cases

Place partner-supplied historical flood case JSON files here for V5 Shadow Mode evaluation.

The folder is intentionally empty of real cases until the partner supplies documented material.

## Required separation

Each case contains:
1. evidence that was available at or before an explicit evidence cutoff; and
2. the later documented outcome.

The later outcome is evaluator-only and must not be sent to Evidence, Risk, Decision, Critic, or LLM reasoning calls.

This prevents hindsight leakage during retrospective evaluation.

## Evidence examples

A case may contain official bulletins, rainfall observations, sensor reports, road-status records, maps, citizen reports/photos, or other documented evidence. Source quality is recorded explicitly; it must not be treated as a calibrated probability unless independently justified.

## LLM use

V5 will allow the Evidence and Critic agents to consume the cutoff-safe evidence package through structured Pydantic contracts. Invalid/failed LLM output must use retry and deterministic fallback. Safety remains deterministic.

Do not commit confidential, private, personally identifying, or improperly licensed field data.
