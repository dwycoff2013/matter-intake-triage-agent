# Matter Intake Triage Agent Architecture

This document describes the multi-agent architecture for the Legal Matter Intake system using Google ADK 2.0.

## Overview

The system uses a hierarchical agent pattern orchestrated by a `Coordinator Agent`.
```
  Coordinator Agent
     |
     +-- Intake Classifier Agent
     |     - classifies matter type and urgency
     |
     +-- Document Extraction Agent
     |     - extracts parties, dates, locations, documents, claims
     |
     +-- Deadline Triage Agent
     |     - calculates date intervals
     |     - flags uncertainty
     |     - requires human verification
     |
     +-- Security & Compliance Agent
     |     - redacts PII
     |     - blocks legal-advice requests
     |     - records tool calls
     |
     +-- Packet Writer Agent
           - generates structured intake memo
           - generates missing-info checklist
```

## Data Flow
1. User provides intake text to the Coordinator.
2. The Coordinator delegates to the Security Reviewer for PII redaction and policy compliance.
3. The Coordinator sends the sanitized text to the Intake Classifier and Document Extractor.
4. Extracted dates are passed to the Deadline Triage agent for interval calculation and calendar event generation.
5. All findings are synthesized by the Packet Writer agent.

## Deterministic Boundaries and Agent Reliability

LexTriage is designed as a workflow coordinator, not a general chatbot. The coordinator routes a legal intake through reviewable stages so that high-risk decisions are handled by deterministic tools and human review rather than hidden model behavior.

```text
START
  -> Security / PII / Prompt-Injection Gate
  -> Matter Classification
  -> Document and Date Extraction
  -> Deadline Triage
  -> Policy Lookup
  -> Packet Writer
  -> Human Review
```

Security review happens first. Raw intake text may contain PII, confidential facts, legal-advice requests, or prompt-injection language, so the raw text should not be broadcast to every subagent. Instead, the security gate redacts or flags sensitive content, and downstream agents receive the smallest useful context for their role.

Deterministic MCP-style local tools provide explicit boundaries for redaction, date extraction, date math, audit logging, and policy lookup. These tool calls are easy to test, replay, and inspect in trajectory evaluations. The packet writer composes structured intermediate outputs into a human-reviewable intake packet.

Human review is required for legal-advice requests, prompt-injection attempts, sensitive matters, and urgent deadlines. The final packet is an intake aid for review by qualified personnel, not legal advice or a substitute for attorney judgment.
