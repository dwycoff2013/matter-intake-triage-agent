from google.adk.tools import ToolContext

def lookup_mock_matter_type_policy(matter_type: str) -> dict:
    """Looks up the policy guidelines for a specific legal matter type.
    
    Args:
        matter_type: The type of legal matter (e.g., 'Litigation', 'Corporate', 'Real Estate').
        
    Returns:
        dict containing the policy guidelines.
    """
    mock_policies = {
        "Litigation": "Requires immediate deadline triage and preservation notices.",
        "Corporate": "Standard 3-day SLA for document extraction.",
        "Real Estate": "Check for local jurisdiction requirements.",
    }
    
    policy = mock_policies.get(matter_type, "Standard general intake policy applies.")
    
    return {"status": "success", "matter_type": matter_type, "policy": policy}
