from pydantic import BaseModel, Field
from google.adk.agents import Agent
from app.tools.dates import calculate_days_between_dates, extract_dates_regex
from app.tools.mock_calendar import create_mock_calendar_event

class DeadlineTriageOutput(BaseModel):
    calculated_deadlines: list[str] = Field(description="List of calculated deadlines")
    uncertainty_flag: bool = Field(description="True if there is uncertainty requiring human verification")
    calendar_events_created: list[str] = Field(description="IDs or summaries of created calendar events")

deadline_triage = Agent(
    name="deadline_triage",
    model="gemini-1.5-flash",
    mode="task",
    tools=[calculate_days_between_dates, extract_dates_regex, create_mock_calendar_event],
    output_schema=DeadlineTriageOutput,
    description="Calculates date intervals for deadlines, flags uncertainty, and creates calendar events.",
    instruction="""You calculate deadlines based on dates found in the text.
    Use the provided date tools to extract and calculate intervals.
    If a deadline is identified, use the calendar tool to create an event.
    If any dates or intervals are ambiguous, set uncertainty_flag to true.
    Call finish_task when done."""
)
