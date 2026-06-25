# LexTriage Protocol Demonstrations

LexTriage uses lightweight, local protocol demonstrations to make the agent architecture easier to inspect and evaluate without live credentials, real client data, or deployment infrastructure.

## ADK-compatible agent implementation

The root coordinator and subagents are implemented with the Google Agent Development Kit (ADK) shape used elsewhere in this repository. The coordinator delegates to specialist agents for security review, intake classification, document extraction, deadline triage, and packet writing.

## MCP-style deterministic local tools

The repository keeps deterministic functions at tool boundaries: redaction, date extraction, mock calendar checks, mock policy lookup, and audit logging. These tools are MCP-style in the architectural sense that they create narrow, inspectable, deterministic interfaces between agent reasoning and local capabilities.

## A2A-style Agent Cards and task envelopes

`app/protocols/a2a.py` defines local dataclasses for Agent Cards, skills, task envelopes, and response envelopes. `app/protocols/a2a_router.py` uses those models to produce a reproducible routing trace:

1. coordinator to security reviewer;
2. coordinator to intake classifier;
3. coordinator to document extractor;
4. coordinator to deadline triage;
5. coordinator to packet writer.

This demonstrates agent interoperability metadata and evaluation-friendly task traces. It is not a production A2A server and does not perform network dispatch.

## A2UI-style structured intake interface

`app/ui/a2ui_payloads.py` builds JSON-serializable payloads with components such as risk banners, matter summaries, deadline timelines, safety flags, missing-information checklists, recommended actions, and human-review disclaimers.

This is an A2UI-style structured payload for human-reviewable legal intake. It should not be read as a claim of official A2UI compliance or certification.

## Protocol-aware evaluation

The local evaluation harness preserves existing quality metrics and adds protocol metrics for A2A trace completion, security-first routing, A2UI schema validity, human-review disclaimers, and risk banners.
