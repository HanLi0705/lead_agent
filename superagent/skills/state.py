"""State management for skills middleware.

This module defines the state types used by the SkillsMiddleware to manage
skills metadata throughout the agent execution lifecycle.
"""

from typing import NotRequired, TypedDict, List
from langchain.agents.middleware.types import AgentState
from .load import SkillMetadata


class SkillsState(AgentState):
    """State for skills middleware.
    
    This state holds the skills metadata that is loaded from user and project
    skill directories. The state is updated before each agent execution to
    ensure the most current skills are available.
    """
    skills_metadata: NotRequired[List[SkillMetadata]]


class SkillsStateUpdate(TypedDict, total=False):
    """Update for skills state.
    
    Used to update the skills state with new skills metadata. This allows
    partial updates to the state.
    """
    skills_metadata: List[SkillMetadata]
