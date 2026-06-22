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
