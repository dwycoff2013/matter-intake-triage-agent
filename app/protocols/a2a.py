"""Lightweight A2A-style protocol models for local LexTriage demos.

These dataclasses intentionally avoid network clients and live credentials. They
model Agent Cards, skills, and task/response envelopes closely enough for a
reproducible notebook demonstration of protocol-aware routing.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

JSON = dict[str, Any]


@dataclass(frozen=True)
class AgentSkill:
    """A locally advertised capability on an A2A-style Agent Card."""

    id: str
    name: str
    description: str
    input_modes: list[str] = field(default_factory=lambda: ["text/plain", "application/json"])
    output_modes: list[str] = field(default_factory=lambda: ["application/json"])

    def to_dict(self) -> JSON:
        return asdict(self)


@dataclass(frozen=True)
class AgentCard:
    """A2A-style description of an interoperable LexTriage agent."""

    id: str
    name: str
    description: str
    version: str
    skills: list[AgentSkill]
    input_modes: list[str]
    output_modes: list[str]
    security_requirements: list[str]

    def to_dict(self) -> JSON:
        data = asdict(self)
        data["skills"] = [skill.to_dict() for skill in self.skills]
        return data


@dataclass(frozen=True)
class A2ATaskEnvelope:
    """Local A2A-style task request passed between demo agents."""

    id: str
    from_agent: str
    to_agent: str
    task_id: str
    case_id: str
    skill_id: str
    payload: JSON
    input_mode: str = "application/json"
    output_mode: str = "application/json"
    status: str = "submitted"

    def to_dict(self) -> JSON:
        return asdict(self)


@dataclass(frozen=True)
class A2AResponseEnvelope:
    """Local A2A-style task response returned by a demo subagent."""

    id: str
    from_agent: str
    to_agent: str
    task_id: str
    case_id: str
    skill_id: str
    payload: JSON
    status: str = "completed"
    input_mode: str = "application/json"
    output_mode: str = "application/json"

    def to_dict(self) -> JSON:
        return asdict(self)


def _skill(skill_id: str, name: str, description: str, output_modes: list[str] | None = None) -> AgentSkill:
    return AgentSkill(
        id=skill_id,
        name=name,
        description=description,
        output_modes=output_modes or ["application/json"],
    )


def build_lextriage_agent_cards() -> dict[str, AgentCard]:
    """Build local A2A-style Agent Cards for the LexTriage agent graph."""

    common_inputs = ["text/plain", "application/json"]
    common_outputs = [
        "application/json",
        "application/vnd.lextriage.packet+json",
        "application/vnd.lextriage.ui+json",
    ]
    local_security = ["local-only", "synthetic-data-only", "no-live-credentials", "pii-minimization"]
    return {
        "coordinator": AgentCard(
            id="coordinator",
            name="LexTriage Coordinator",
            description="Routes legal intake work through security-first subagent tasks.",
            version="1.0.0",
            skills=[
                _skill("route_intake", "Route Intake", "Delegate intake tasks in a deterministic security-first order."),
                _skill("compose_trace", "Compose Routing Trace", "Record A2A-style task envelopes for evaluation."),
            ],
            input_modes=common_inputs,
            output_modes=common_outputs,
            security_requirements=local_security,
        ),
        "security_reviewer": AgentCard(
            id="security_reviewer",
            name="Security Reviewer",
            description="Redacts PII and detects legal-advice and prompt-injection risk before other agents run.",
            version="1.0.0",
            skills=[
                _skill("redact_pii", "Redact PII", "Remove demo emails, phones, SSNs, and card-like numbers."),
                _skill("detect_legal_advice_request", "Detect Legal Advice Request", "Flag requests for legal strategy or guarantees."),
                _skill("detect_prompt_injection", "Detect Prompt Injection", "Flag attempts to override system safeguards."),
            ],
            input_modes=common_inputs,
            output_modes=["application/json"],
            security_requirements=local_security,
        ),
        "intake_classifier": AgentCard(
            id="intake_classifier",
            name="Intake Classifier",
            description="Classifies matter area, subtype, urgency, and human-review needs.",
            version="1.0.0",
            skills=[
                _skill("classify_matter", "Classify Matter", "Identify matter area and subtype."),
                _skill("estimate_urgency", "Estimate Urgency", "Map deadlines and risk flags to urgency labels."),
            ],
            input_modes=common_inputs,
            output_modes=["application/json"],
            security_requirements=local_security,
        ),
        "document_extractor": AgentCard(
            id="document_extractor",
            name="Document Extractor",
            description="Extracts parties, notices, dates, and missing information from intake text.",
            version="1.0.0",
            skills=[
                _skill("extract_entities", "Extract Entities", "Extract demo parties and document references."),
                _skill("identify_missing_information", "Identify Missing Information", "Build a checklist for follow-up."),
            ],
            input_modes=common_inputs,
            output_modes=["application/json"],
            security_requirements=local_security,
        ),
        "deadline_triage": AgentCard(
            id="deadline_triage",
            name="Deadline Triage",
            description="Extracts dates and flags deadline proximity and uncertainty.",
            version="1.0.0",
            skills=[
                _skill("extract_dates", "Extract Dates", "Find explicit dates in synthetic intake text."),
                _skill("calculate_deadline_proximity", "Calculate Deadline Proximity", "Estimate days until a deadline."),
                _skill("flag_deadline_uncertainty", "Flag Deadline Uncertainty", "Identify absent or ambiguous deadlines."),
            ],
            input_modes=common_inputs,
            output_modes=["application/json"],
            security_requirements=local_security,
        ),
        "packet_writer": AgentCard(
            id="packet_writer",
            name="Packet Writer",
            description="Creates human-reviewable intake packets and missing-information checklists.",
            version="1.0.0",
            skills=[
                _skill("create_intake_packet", "Create Intake Packet", "Assemble a structured intake packet.", ["application/vnd.lextriage.packet+json"]),
                _skill("create_missing_information_checklist", "Create Missing Information Checklist", "List missing items for review."),
            ],
            input_modes=common_inputs,
            output_modes=["application/json", "application/vnd.lextriage.packet+json", "application/vnd.lextriage.ui+json"],
            security_requirements=local_security,
        ),
    }
