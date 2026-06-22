from pydantic import BaseModel, Field
from google.adk.agents import Agent
from app.tools.redaction import redact_pii
from app.tools.audit_log import write_audit_log

class SecurityReviewOutput(BaseModel):
    redacted_text: str = Field(description="The text after PII redaction")
    legal_advice_requested: bool = Field(description="True if the user is seeking legal advice")
    compliance_flags: list[str] = Field(description="Any compliance issues found")

security_reviewer = Agent(
    name="security_reviewer",
    model="gemini-1.5-flash",
    mode="task",
    tools=[redact_pii, write_audit_log],
    output_schema=SecurityReviewOutput,
    description="Redacts PII, blocks legal advice requests, and writes audit logs.",
    instruction="""You are the Security and Compliance Reviewer.
    1. Check if the input asks for legal advice. If so, set legal_advice_requested to true.
    2. Use the redact_pii tool to clean the input text of personal information.
    3. Write an audit log using the write_audit_log tool noting the redaction and compliance check.
    Call finish_task with your results when done."""
)
