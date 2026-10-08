# V6 Experimental — Human Baseline & Retrospective Shadow Mode

**Hackathon-first:** V6 is a small evaluation layer on the existing V5 multi-agent workflow, not a replacement for Context/Evidence → Risk/Decision → Critic → Safety → Human Gate → Explanation.

## Research question
Do AI recommendations and escalations remain useful and traceable when compared with independent human judgments using the same historical evidence cutoff?

## Sprint-style milestones and acceptance criteria
1. **Baseline:** preserve V5 on its own branch; V6 branch is independent.
2. **Historical evidence:** every case has a timestamped evidence cutoff and source IDs; unknown-time or post-cutoff evidence is excluded from V6 snapshot.
3. **Human baseline:** independent reviewer submits priority, escalation, rationale, evidence IDs, and measured review time without seeing later outcome.
4. **Shadow run:** run existing multi-agent graph without taking operational action; store trace, priority, safety status and workflow duration.
5. **Evaluation:** report agreement, disagreements, review burden, and timing. Label missed/unnecessary escalations **only after independent adjudication**, not from AI-human disagreement alone.

## Important limitations
- Retrospective shadow mode is NOT a prospective operational pilot.
- The current V6 mapper only consumes explicitly structured `rainfall_mm` and `road_status` fields; other field context is not automatically inferred.
- V5 field context lacks individual observation timestamps, so V6 conservatively excludes it until timestamped provenance is introduced.
- A documented later outcome is evaluator-only and never passed to the graph.
- Human baseline is a real independent review record, NOT the synthetic manual_baseline heuristic from V4/V5.
- Current implementation does not yet expose a V6 GUI tab or live Gemini integration.
- No emergency action, dispatch or road closure is performed.
- No claim of real-world accuracy or readiness is warranted by synthetic cases.

## Usage
Prepare a field-case JSON matching `resilientcity.field_cases.FieldCase` and a blinded human-review JSON matching `resilientcity.shadow_mode.HumanBaseline`.

```python
from resilientcity.shadow_mode import evaluate_pair
result = evaluate_pair("case.json", "human_review.json")
print(result)
```

## Next only if hackathon schedule permits
Add an optional evaluation GUI panel, case-by-case adjudication, and timestamped contextual inputs. Preserve strong multi-agent demonstration as priority.

**AI recommends. AI explains. Humans decide.**
