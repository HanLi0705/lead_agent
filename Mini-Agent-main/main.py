import asyncio
import os
from pathlib import Path
from mini_agent import Agent, LLMClient, LLMProvider
from mini_agent.config import Config
from mini_agent.cli import initialize_base_tools, add_workspace_tools

async def main():
    # 1. Load configuration
    # Prioritize ~/.mini-agent/config/config.yaml, fallback to project config
    config_path = Config.get_default_config_path()
    if not config_path.exists():
        # Fallback: if none found, try to find config in the repository
        config_path = Path(__file__).parent / "mini_agent" / "config" / "config.yaml"
        if not config_path.exists():
            config_path = Path(__file__).parent / "mini_agent" / "config" / "config-example.yaml"
    
    print(f"Loading config from: {config_path}")
    config = Config.from_yaml(config_path)

    # 2. Initialize LLM Client
    provider = LLMProvider.ANTHROPIC if config.llm.provider.lower() == "anthropic" else LLMProvider.OPENAI
    llm_client = LLMClient(
        api_key=config.llm.api_key,
        provider=provider,
        api_base=config.llm.api_base,
        model=config.llm.model,
        verify=config.llm.verify,
        ssl_ca_path=config.llm.ssl_ca_path,
    )

    # 3. Initialize Tools
    workspace_dir = Path.cwd() / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    tools, skill_loader = await initialize_base_tools(config)
    add_workspace_tools(tools, config, workspace_dir)

    # 4. Set System Prompt
    # You can customize your prompt here
    system_prompt = """You are a helpful and efficient general-purpose AI agent.
You have access to a variety of tools to help you complete tasks.

For any task, especially difficult ones, you MUST follow this workflow:
1. **PLANNING & TODO LIST**: If you encounter a difficult task, you MUST write a structured TODO list first before taking any action.
2. **EXECUTION**: Execute the steps one by one using the appropriate tools.
3. **PROGRESS TRACKING**: After each major step or tool call, update your TODO list (mark items as completed, add new ones if needed) and explain your reasoning for the next action.

**Search Guidelines:**
- When asked to "search" for a signal, keyword, or variable, do NOT only search for filenames. 
- You MUST search INSIDE file contents (e.g., using `grep`) because technical identifiers (like signal names) are often contained within files (especially in .svg, .c, .h, .xml files) while the filenames might be generic.

Always report your progress and state of the TODO list clearly to the user."""

    if skill_loader:
        skills_metadata = skill_loader.get_skills_metadata_prompt()
        if skills_metadata:
            system_prompt += f"\n\n## Available Skills\n{skills_metadata}"

    # 5. Create Agent
    agent = Agent(
        llm_client=llm_client,
        system_prompt=system_prompt,
        tools=tools,
        max_steps=config.agent.max_steps,
        workspace_dir=str(workspace_dir),
        verbose=True,  
    )

    # 6. Run Test
    # Enter your test prompt here
    test_prompt = "this is difficult task.please search stDFCHeatrAvlChk /home/lihan/project/llm_application/agents/documentation,if the results has .svg files, please analyze those .svg files, please write the report about how this signal work and what effect this signal, make sure write file to .md file."
    
    print(f"\n🚀 Running Agent with prompt: {test_prompt}")
    agent.add_user_message(test_prompt)
    
    response = await agent.run()
    
    print("\n" + "="*60)
    print("Final Response:")
    print(response)
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
