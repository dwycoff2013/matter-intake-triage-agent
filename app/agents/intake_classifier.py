from pydantic import BaseModel, Field
from google.adk.agents import Agent

class ClassificationOutput(BaseModel):
    matter_type: str = Field(description="The type of the legal matter (e.g., Litigation, Corporate)")
    urgency: str = Field(description="The urgency level: Low, Medium, High")
    summary: str = Field(description="A brief summary of the matter")

intake_classifier = Agent(
    name="intake_classifier",
    model="gemini-1.5-flash",
    mode="task",
    output_schema=ClassificationOutput,
    description="Classifies the matter type and urgency of an intake email or document.",
    instruction="""You are an expert legal intake classifier. 
    Analyze the provided text to determine the matter type and its urgency.
    Call finish_task with your structured classification when done."""
)
