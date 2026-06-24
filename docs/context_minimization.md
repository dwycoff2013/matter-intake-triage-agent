# Context Minimization

Legal intake workflows should pass the minimum necessary context to each agent. This reduces unnecessary exposure of confidential facts, improves auditability, and makes failures easier to isolate.

- **Security reviewer:** receives raw intake first because it must detect PII, prompt injection, and legal-advice requests.
- **Classifier:** receives redacted intake plus metadata such as detected risk flags and high-level dates.
- **Deadline triage:** receives extracted dates, normalized deadline candidates, and trigger phrases rather than the full narrative where possible.
- **Packet writer:** receives structured intermediate outputs: classification, redaction summary, extracted dates, checklist items, and review flags.
- **Audit log:** receives event metadata, tool names, status, and routing decisions, not raw confidential text where avoidable.

This context-minimization design is a differentiator for legal-ops agents because it treats confidentiality and reviewability as workflow properties rather than prompt-only instructions.
