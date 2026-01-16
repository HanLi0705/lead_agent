"""Agent management and creation for superagent"""

import logging
import os
from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend
from langchain.agents.middleware import InterruptOnConfig
from langchain.agents.middleware.types import AgentState
from langchain.messages import ToolCall
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.pregel import Pregel
from langgraph.runtime import Runtime

from .prompt import get_system_prompt
from .agent_memory import create_agent_memory_middleware
from .skills.middleware import SkillsMiddleware
from .middleware.shell import ShellMiddleware



logger = logging.getLogger("superagent")


def _format_write_file_description(
    tool_call: ToolCall, _state: AgentState, _runtime: Runtime
) -> str:
    """Format write_file tool call for approval prompt."""
    args = tool_call["args"]
    file_path = args.get("file_path", "unknown")
    content = args.get("content", "")

    action = "Overwrite" if Path(file_path).exists() else "Create"
    line_count = len(content.splitlines())

    return f"File: {file_path}\nAction: {action} file\nLines: {line_count}"


def _format_edit_file_description(
    tool_call: ToolCall, _state: AgentState, _runtime: Runtime
) -> str:
    """Format edit_file tool call for approval prompt."""
    args = tool_call["args"]
    file_path = args.get("file_path", "unknown")
    replace_all = bool(args.get("replace_all", False))

    return (
        f"File: {file_path}\n"
        f"Action: Replace text ({'all occurrences' if replace_all else 'single occurrence'})"
    )


def _format_task_description(tool_call: ToolCall, _state: AgentState, _runtime: Runtime) -> str:
    """Format task (subagent) tool call for approval prompt.

    The task tool signature is: task(description: str, subagent_type: str)
    The description contains all instructions that will be sent to the subagent.
    """
    args = tool_call["args"]
    description = args.get("description", "unknown")
    subagent_type = args.get("subagent_type", "unknown")

    # Truncate description if too long for display
    description_preview = description
    if len(description) > 500:
        description_preview = description[:500] + "..."

    return (
        f"Subagent Type: {subagent_type}\n\n"
        f"Task Instructions:\n"
        f"{'─' * 40}\n"
        f"{description_preview}\n"
        f"{'─' * 40}\n\n"
        f"⚠️  Subagent will have access to file operations and shell commands"
    )


def _format_shell_description(tool_call: ToolCall, _state: AgentState, _runtime: Runtime) -> str:
    """Format shell tool call for approval prompt."""
    args = tool_call["args"]
    command = args.get("command", "N/A")
    return f"Shell Command: {command}\nWorking Directory: {Path.cwd()}"


def _format_web_search_description(
    tool_call: ToolCall, _state: AgentState, _runtime: Runtime
) -> str:
    """Format web_search tool call for approval prompt."""
    args = tool_call["args"]
    query = args.get("query", "unknown")
    max_results = args.get("max_results", 5)

    return f"Query: {query}\nMax results: {max_results}\n\n⚠️  This will use Tavily API credits"


def _format_fetch_url_description(
    tool_call: ToolCall, _state: AgentState, _runtime: Runtime
) -> str:
    """Format fetch_url tool call for approval prompt."""
    args = tool_call["args"]
    url = args.get("url", "unknown")
    timeout = args.get("timeout", 30)

    return f"URL: {url}\nTimeout: {timeout}s\n\n⚠️  Will fetch and convert web content to markdown"


def _format_execute_description(
    tool_call: ToolCall, _state: AgentState, _runtime: Runtime
) -> str:
    """Format execute tool call for approval prompt."""
    args = tool_call["args"]
    command = args.get("command", "N/A")
    return f"Execute Command: {command}\nLocation: Remote Sandbox"


def _add_interrupt_on() -> dict[str, InterruptOnConfig]:
    """Configure human-in-the-loop interrupt_on settings for destructive tools."""
    shell_interrupt_config: InterruptOnConfig = {
        "allowed_decisions": ["approve", "reject"],
        "description": _format_shell_description,
    }

    execute_interrupt_config: InterruptOnConfig = {
        "allowed_decisions": ["approve", "reject"],
        "description": _format_execute_description,
    }

    write_file_interrupt_config: InterruptOnConfig = {
        "allowed_decisions": ["approve", "reject"],
        "description": _format_write_file_description,
    }

    edit_file_interrupt_config: InterruptOnConfig = {
        "allowed_decisions": ["approve", "reject"],
        "description": _format_edit_file_description,
    }

    web_search_interrupt_config: InterruptOnConfig = {
        "allowed_decisions": ["approve", "reject"],
        "description": _format_web_search_description,
    }

    fetch_url_interrupt_config: InterruptOnConfig = {
        "allowed_decisions": ["approve", "reject"],
        "description": _format_fetch_url_description,
    }

    task_interrupt_config: InterruptOnConfig = {
        "allowed_decisions": ["approve", "reject"],
        "description": _format_task_description,
    }

    return {
        "shell": shell_interrupt_config,
        "execute": execute_interrupt_config,
        "write_file": write_file_interrupt_config,
        "edit_file": edit_file_interrupt_config,
        "web_search": web_search_interrupt_config,
        "fetch_url": fetch_url_interrupt_config,
        "task": task_interrupt_config,
    }


def create_superagent(
    model: str | BaseChatModel,
    working_dir: Path | str | None = None,
    *,
    tools: list[Any] | None = None,
    system_prompt: str | None = None,
    auto_approve: bool = False,
    enable_subagents: bool = True,
    enable_memory: bool = True,
    enable_skills: bool = True,
    enable_shell: bool = True,
    assistant_id: str = "superagent",
) -> tuple[Pregel, CompositeBackend]:
    """Create a superagent with flexible options.

    Args:
        model: LLM model to use (e.g., "anthropic:claude-sonnet-4-5-20250929" or ChatAnthropic instance)
        working_dir: Working directory for file operations (defaults to current directory)
        tools: Additional tools to provide to agent (default: empty list)
        system_prompt: Override the default system prompt. If None, generates one based on working_dir.
        auto_approve: If True, automatically approves all tool calls without human confirmation.
        enable_subagents: Whether to enable subagent functionality (default True)
        enable_memory: Whether to enable long-term memory functionality (default True)
        enable_skills: Whether to enable skills functionality (default True)
        enable_shell: Whether to enable shell functionality (default True)
        assistant_id: Agent identifier for memory storage (default "superagent")

    Returns:
        2-tuple of (agent_graph, composite_backend)
        - agent_graph: Configured LangGraph Pregel instance ready for execution
        - composite_backend: CompositeBackend for file operations
    """
    if tools is None:
        tools = []

    if working_dir is None:
        working_dir = Path.cwd()
    else:
        working_dir = Path(working_dir).resolve()

    logger.info(f"Working directory set to: {working_dir}")

    # Get or use custom system prompt
    if system_prompt is None:
        system_prompt = get_system_prompt(working_dir)

    logger.info(f"System prompt length: {len(system_prompt)} characters")
    logger.info(f"System prompt: {system_prompt}")

    # Set up backend (using local filesystem)
    backend = CompositeBackend(
        default=FilesystemBackend(),
        routes={},
    )

    # Configure interrupt_on based on auto_approve setting
    if auto_approve:
        # No interrupts - all tools run automatically
        interrupt_on = {}
    else:
        # Full HITL for destructive operations
        interrupt_on = _add_interrupt_on()

    # Configure subagents
    if not enable_subagents:
        subagents = []
    else:
        # Explicitly configure only general-purpose subagent
        subagents = [
            {
                "name": "general-purpose",
                "description": "General purpose subagent for all tasks",
                "system_prompt": "You are a general-purpose subagent that can handle various tasks including coding, research, and analysis. You will receive a task description from the main agent. Analyze this task carefully and execute it to the best of your ability. ",
            }
        ]

    # Configure middleware stack
    middleware = []
    
    # Add skills if enabled
    if enable_skills:
        # Use relative path from the current file's directory (superagent/agent_skills)
        project_skills_dir = Path(__file__).parent / "agent_skills"
        user_skills_dir = Path.home() / ".superagent" / "skills"
        
        # Ensure directories exist
        project_skills_dir.mkdir(parents=True, exist_ok=True)
        user_skills_dir.mkdir(parents=True, exist_ok=True)
        
        # SkillMiddleware handles progressive disclosure (only injects name/description)
        skills_middleware = SkillsMiddleware(
            user_skills_dir=user_skills_dir,
            project_skills_dir=project_skills_dir
        )
        middleware.append(skills_middleware)
        
        # Log loaded skills for debugging
        from .skills.load import list_skills
        loaded_skills = list_skills(user_skills_dir, project_skills_dir)
        logger.info(f"Skills middleware enabled. Loaded {len(loaded_skills)} skills")
        for s in loaded_skills:
            logger.info(f" - Skill: {s['name']}")

    # Add memory middleware if enabled
    if enable_memory:
        # Create agent memory middleware
        memory_middleware = create_agent_memory_middleware(
            assistant_id=assistant_id,
            project_root=working_dir,
        )
        middleware.append(memory_middleware)
        logger.info(f"Memory middleware enabled for assistant: {assistant_id}")

    # Add shell middleware if enabled
    if enable_shell:
        # Create environment for shell commands
        shell_env = os.environ.copy()
        
        shell_middleware = ShellMiddleware(
            workspace_root=working_dir,
            env=shell_env,
        )
        middleware.append(shell_middleware)
        logger.warning(
            "SECURITY WARNING: Shell tool is enabled. The agent can execute arbitrary commands on your local machine. "
            "Shell commands will execute automatically once the agent invokes them. "
            "To disable this feature, set enable_shell=False when creating the agent."
        )
        logger.info(f"Shell middleware enabled with working directory: {working_dir}")

    # Create the agent
    # create_deep_agent automatically adds:
    # - TodoListMiddleware (provides write_todos tool)
    # - FilesystemMiddleware (provides ls, read_file, write_file, edit_file, glob, grep)
    # - SubAgentMiddleware (provides task tool, if enable_subagents=True)
    # - SummarizationMiddleware (automatically compresses long history)
    agent = create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        tools=tools,
        backend=backend,
        subagents=subagents,
        interrupt_on=interrupt_on,
        checkpointer=InMemorySaver(),
        middleware=middleware,
    ).with_config({"recursion_limit": 1000})

    return agent, backend


def create_simple_agent(
    model: str | BaseChatModel,
    working_dir: Path | str | None = None,
    *,
    auto_approve: bool = False,
    enable_subagents: bool = True,
    enable_memory: bool = True,
    enable_skills: bool = True,
    enable_shell: bool = True,
    assistant_id: str = "superagent",
) -> Pregel:
    """Create a simple general-purpose agent

    Args:
        model: LLM model (e.g., "anthropic:claude-sonnet-4-5-20250929" or ChatAnthropic instance)
        working_dir: Working directory (defaults to current directory)
        auto_approve: Whether to auto-approve all tool calls (default False, requires manual approval for dangerous operations)
        enable_subagents: Whether to enable subagent functionality (default True)
        enable_memory: Whether to enable long-term memory functionality (default True)
        enable_skills: Whether to enable skills functionality (default True)
        enable_shell: Whether to enable shell functionality (default True)
        assistant_id: Agent identifier for memory storage (default "superagent")

    Returns:
        Configured agent graph
    """
    agent, _ = create_superagent(
        model=model,
        working_dir=working_dir,
        auto_approve=auto_approve,
        enable_subagents=enable_subagents,
        enable_memory=enable_memory,
        enable_skills=enable_skills,
        enable_shell=enable_shell,
        assistant_id=assistant_id,
    )
    return agent


def run_interactive(agent: Pregel) -> None:
    """Run agent in interactive mode

    Args:
        agent: Configured agent instance
    """
    # TODO: Implement interactive mode similar to deepagents-cli
    print("Interactive mode not yet implemented")
    print("Use agent.invoke() for single execution")