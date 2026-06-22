from pydantic import BaseModel, Field
from google.adk.agents import Agent

class DocumentExtractionOutput(BaseModel):
    parties: list[str] = Field(description="List of parties involved")
    dates: list[str] = Field(description="Important dates found in the document")
    locations: list[str] = Field(description="Locations mentioned")
    documents_referenced: list[str] = Field(description="Names or types of documents referenced")
    claims: list[str] = Field(description="Legal claims or issues identified")

document_extractor = Agent(
    name="document_extractor",
    model="gemini-1.5-flash",
    mode="task",
    output_schema=DocumentExtractionOutput,
    description="Extracts key entities like parties, dates, locations, documents, and claims.",
    instruction="""You are a precise legal document extraction assistant.
    Analyze the text and extract the required information into structured fields.
    Call finish_task with your findings when done."""
)
