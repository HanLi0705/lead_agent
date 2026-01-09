"""Middleware for loading and exposing agent skills to the system prompt.

This middleware implements the "Agent Skills" pattern with progressive disclosure:
1. Parse YAML frontmatter from SKILL.md files at session start
2. Inject skills metadata (name + description) into system prompt
3. Agent reads full SKILL.md content when relevant to a task via read_file

This implementation uses a state-based approach similar to DeepAgents-CLI,
with dynamic skill reloading on each agent execution.
"""

import logging
from pathlib import Path
from typing import Optional, Callable, Any
from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langgraph.runtime import Runtime
from .load import SkillMetadata, list_skills
from .state import SkillsState, SkillsStateUpdate

logger = logging.getLogger("superagent.skills")

SKILLS_SYSTEM_PROMPT = """
## 🧩 SKILL SYSTEM - CRITICAL PROTOCOL

You have access to specialized skills that contain expert knowledge, workflows, and tools for specific tasks. **Using the right skill is ESSENTIAL for providing accurate and efficient responses.**

### 🎯 WHEN TO CHECK SKILLS (MANDATORY)

**ALWAYS check the available skills list FIRST when:**
- The user mentions specific domains (arXiv, research, papers, documentation, etc.)
- The task requires specialized knowledge or workflows
- The user asks for search, analysis, or processing of specific types of content
- You recognize a pattern that matches a skill's description
- You're unsure how to proceed with a task

### 📋 SKILL USAGE PROTOCOL

1. **IDENTIFY**: Review the "Available Skills" list below
2. **MATCH**: Find the skill that best matches the user's request
3. **READ**: Use `read_file` tool with the **exact absolute path** provided to read the FULL SKILL.md documentation
   - ⚠️ DO NOT use `ls`, `grep`, or other search tools to find skill files
   - ⚠️ Use the path exactly as shown in the skills list
4. **EXECUTE**: Follow the skill's instructions, workflows, and procedures exactly
5. **REPORT**: Provide results based on the skill's output format

### ⚠️ CRITICAL RULES

- **FIRST PRIORITY**: If a relevant skill exists, reading its SKILL.md is your FIRST action
- **NO GUESSING**: Never attempt to implement functionality that a skill already provides
- **FOLLOW INSTRUCTIONS**: Skills contain expert knowledge - follow them precisely
- **EFFICIENCY**: Using the right skill saves time and provides better results

### 📚 AVAILABLE SKILLS

{skills_list}

---

**REMINDER**: Before attempting any complex task, ALWAYS check if a skill exists for it. Skills contain specialized knowledge and workflows that you should leverage.**
"""


class SkillsMiddleware(AgentMiddleware):
    """Middleware to inject available skills into the system prompt.
    
    This middleware uses a state-based approach where skills are dynamically
    loaded on each agent execution, allowing for real-time updates to the
    skills directories.
    """

    state_schema = SkillsState
    
    def __init__(
        self,
        user_skills_dir: Optional[Path] = None,
        project_skills_dir: Optional[Path] = None,
    ):
        self.user_skills_dir = user_skills_dir
        self.project_skills_dir = project_skills_dir

    def before_agent(self, state: AgentState, runtime: Runtime) -> SkillsStateUpdate | None:
        """Load skills metadata before agent execution.
        
        This runs before each agent execution to discover available skills from both
        user-level and project-level directories. Skills are re-loaded on every
        interaction to capture any changes in the skills directories.
        
        Args:
            state: Current agent state
            runtime: Runtime instance for agent execution
            
        Returns:
            SkillsStateUpdate with the latest skills metadata, or None if no skills found
        """
        logger.info("=" * 80)
        logger.info("🔍 SkillsMiddleware: before_agent called")
        logger.info(f"   User skills dir: {self.user_skills_dir}")
        logger.info(f"   Project skills dir: {self.project_skills_dir}")
        
        skills = list_skills(
            user_skills_dir=self.user_skills_dir,
            project_skills_dir=self.project_skills_dir,
        )
        
        logger.info(f"   Loaded {len(skills)} skills:")
        for i, skill in enumerate(skills, 1):
            logger.info(f"     {i}. {skill['name']}: {skill['description']}")
            logger.info(f"        Path: {skill['path']}")
            logger.info(f"        Source: {skill['source']}")
        
        logger.info(f"   Current state keys: {list(state.keys())}")
        logger.info(f"   State before update: {state}")
        logger.info("=" * 80)
        
        if not skills:
            logger.warning("   ⚠️  No skills found, returning None")
            return None
            
        return SkillsStateUpdate(skills_metadata=skills)

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Inject skills info into system prompt.
        
        This method retrieves skills from the state and injects them into the
        system prompt. The skills are obtained from the state that was updated
        by the before_agent method.
        
        Args:
            request: The model request to be processed
            handler: The handler function to call with the modified request
            
        Returns:
            ModelResponse with skills information injected into the system prompt
        """
        logger.info("=" * 80)
        logger.info("🎯 SkillsMiddleware: wrap_model_call called")
        logger.info(f"   Request state keys: {list(request.state.keys())}")
        
        skills = request.state.get("skills_metadata", [])
        
        logger.info(f"   Skills from state: {len(skills)} skills found")
        
        if not skills:
            logger.warning("   ⚠️  No skills in state, skipping skill injection")
            logger.info("=" * 80)
            return handler(request)
            
        skills_list_str = ""
        for skill in skills:
            skills_list_str += f"- **{skill['name']}**: {skill['description']}\n"
            skills_list_str += f"  → Path: `{skill['path']}`\n"
        
        logger.info(f"   Injecting skills into system prompt:")
        logger.info(f"   Skills list:\n{skills_list_str}")
            
        skills_section = SKILLS_SYSTEM_PROMPT.format(skills_list=skills_list_str)
        
        original_prompt_length = len(request.system_prompt or "")
        new_system_prompt = (request.system_prompt or "") + "\n" + skills_section
        new_prompt_length = len(new_system_prompt)
        
        logger.info(f"   Original system prompt length: {original_prompt_length}")
        logger.info(f"   New system prompt length: {new_prompt_length}")
        logger.info(f"   Added {new_prompt_length - original_prompt_length} characters")
        logger.info("=" * 80)
        
        return handler(request.override(system_prompt=new_system_prompt))
