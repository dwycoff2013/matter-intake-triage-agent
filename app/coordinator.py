from google.adk.agents import Agent
from app.agents.intake_classifier import intake_classifier
from app.agents.document_extractor import document_extractor
from app.agents.deadline_triage import deadline_triage
from app.agents.security_reviewer import security_reviewer
from app.agents.packet_writer import packet_writer

coordinator_agent = Agent(
    name="coordinator",
    model="gemini-1.5-flash",
    description="The main coordinator agent that delegates tasks to handle legal matter intake.",
    instruction="""You are the Coordinator Agent for Legal Matter Intake.
    Your job is to process incoming legal matters by delegating to your sub-agents in this general order:
    1. Send to security_reviewer to ensure no PII or legal advice issues.
    2. Send to intake_classifier to determine matter type and urgency.
    3. Send to document_extractor to pull out entities.
    4. Send to deadline_triage to calculate dates.
    5. Send all gathered information to packet_writer to generate the final intake memo.
    
    Coordinate the passing of outputs from one agent to the next to build the final response for the user.""",
    sub_agents=[
        security_reviewer,
        intake_classifier,
        document_extractor,
        deadline_triage,
        packet_writer
    ]
)
