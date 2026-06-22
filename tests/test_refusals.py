import pytest
from app.agents.security_reviewer import security_reviewer

def test_security_reviewer_refusal_logic():
    # Verify the agent is instructed to refuse legal advice requests
    assert "legal advice" in security_reviewer.instruction.lower()
    assert "security" in security_reviewer.name.lower()
