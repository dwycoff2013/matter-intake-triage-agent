from google.adk.tools import ToolContext

def create_mock_calendar_event(title: str, date: str, description: str) -> dict:
    """Creates a mock calendar event for deadline triage.
    
    Args:
        title: The title of the calendar event.
        date: The date for the event (YYYY-MM-DD).
        description: Details about the deadline.
        
    Returns:
        dict with confirmation of the mock event creation.
    """
    event_id = f"evt_{hash(title + date) % 100000}"
    
    # In a real tool, this would call Google Calendar API or similar
    mock_event = {
        "id": event_id,
        "title": title,
        "date": date,
        "description": description,
        "status": "scheduled"
    }
    
    return {"status": "success", "event": mock_event, "message": "Mock calendar event created."}
