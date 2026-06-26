"""ADK CLI wrapper for the LexTriage root agent."""

from app.agent import get_root_agent

root_agent = get_root_agent()

__all__ = ["root_agent"]
