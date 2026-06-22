from pydantic import BaseModel, Field
from google.adk.agents import Agent
from app.tools.mock_policy_lookup import lookup_mock_matter_type_policy

class PacketOutput(BaseModel):
    intake_memo: str = Field(description="The structured intake memo")
    missing_info_checklist: list[str] = Field(description="Checklist of missing information to request")

packet_writer = Agent(
    name="packet_writer",
    model="gemini-1.5-flash",
    mode="task",
    tools=[lookup_mock_matter_type_policy],
    output_schema=PacketOutput,
    description="Generates the final structured intake memo and missing info checklist.",
    instruction="""You are the Packet Writer.
    Take the outputs from the classifier, document extractor, deadline triage, and security review.
    Use the lookup_mock_matter_type_policy tool to get guidelines for the matter type.
    Synthesize all this into a structured intake memo and identify any missing information.
    Call finish_task with the final packet when done."""
)
