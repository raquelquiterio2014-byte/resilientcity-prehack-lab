# Architecture — V4 Experimental Learning Lab

This repository branch is a disposable pre-hackathon learning environment. V3 remains the controlled baseline; V4 deliberately tests harder uncertainty and boundary conditions.

## Multi-agent workflow

Incident -> Planner -> Evidence -> Risk -> Decision -> Critic
                     ^                         |
                     |                         | REVISE
                     +------ Revision <--------+
                                               |
                                      PASS / ESCALATE
                                               v
                                            Safety
                                               v
                                          Human Gate
                                               v
                                            Reporter

## Explicit evidence states

- COMPLETE
- MISSING
- CONTRADICTORY
- OVERLAPPING
- OUT_OF_SCOPE

## Decision space

V4 is not forced to choose LOW / MEDIUM / HIGH. It may also return:
- INSUFFICIENT_EVIDENCE
- UNRESOLVED
- OUT_OF_SCOPE

The Critic can PASS, REVISE, or ESCALATE. The Safety Agent remains deterministic and can approve, approve with limitations, require human review, or block an out-of-scope recommendation.

## Evaluation

The suite contains 20 synthetic scenarios: the original controlled cases plus 12 adversarial/boundary cases. Evaluation includes decision agreement, manual-baseline agreement, evidence traceability, appropriate escalation, missed/unnecessary escalation, insufficient-evidence recognition, contradiction detection, forced-classification rate, workflow time, and reproducibility.

**Workflow validation ≠ real-world readiness.**

These controlled scenarios evaluate architecture behaviour, traceability, escalation, and reproducibility. They do not establish real-world accuracy.

Any future operational pilot must begin in shadow mode, with people making every operational decision.

The lab does not execute emergency actions and does not yet use an LLM, external API, MCP server, sponsor technology, production data, or a calibrated flood-probability model.

**AI recommends. AI explains. Humans decide.**
