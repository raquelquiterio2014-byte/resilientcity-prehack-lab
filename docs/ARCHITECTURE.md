# Architecture — Learning Lab

This repository is a disposable pre-hackathon learning environment.

Current deterministic workflow:

Incident -> Planner -> Evidence -> Risk -> Decision -> Critic
                                      ^          |
                                      |          v
                                   Revision <- REVISE
                                                 |
                                                PASS
                                                 v
                                              Safety -> Reporter -> END

The lab demonstrates specialized responsibilities, shared state, conditional routing, critique, one revision cycle, safety review, human-review escalation, and execution traces.

It intentionally does not execute emergency actions. It also does not yet use an LLM, external API, MCP server, sponsor technology, or production data.

The future competition implementation must be built separately according to the hackathon rules.
