"""
GAIA Evaluation for Mini-Agent

This script evaluates the Mini-Agent on the GAIA benchmark.
"""

import os
import re
import sys
import asyncio
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# Add Mini-Agent-main to path
mini_agent_dir = project_root / "Mini-Agent-main"
sys.path.insert(0, str(mini_agent_dir))

from mini_agent import Agent, LLMClient, LLMProvider
from mini_agent.config import Config
from mini_agent.cli import initialize_base_tools, add_workspace_tools

# GAIA official system prompt
GAIA_SYSTEM_PROMPT = """You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].

YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.

If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.

If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.

If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.

{SKILLS_METADATA}"""

class MiniAgentGAIAWrapper:
    """Wrapper for Mini-Agent to make it compatible with GAIA evaluation tool"""
    
    def __init__(self, workspace_dir: str | None = None):
        """
        Initialize Mini-Agent wrapper
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd() / "gaia_workspace"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Load config
        config_path = Config.get_default_config_path()
        if not config_path.exists():
            # Try to find it in the repository if not found in default locations
            repo_config = mini_agent_dir / "mini_agent" / "config" / "config.yaml"
            if repo_config.exists():
                config_path = repo_config
            else:
                # Use example config if necessary (might need manual API key)
                config_path = mini_agent_dir / "mini_agent" / "config" / "config-example.yaml"
        
        self.config = Config.from_yaml(config_path)
        
        # Initialize LLM with retry support and SSL verification
        from mini_agent.retry import RetryConfig as RetryConfigBase
        
        retry_config = RetryConfigBase(
            enabled=self.config.llm.retry.enabled,
            max_retries=self.config.llm.retry.max_retries,
            initial_delay=self.config.llm.retry.initial_delay,
            max_delay=self.config.llm.retry.max_delay,
            exponential_base=self.config.llm.retry.exponential_base,
            retryable_exceptions=(Exception,),
        )

        def on_retry(exception: Exception, attempt: int):
            print(f"\n⚠️  LLM call failed (attempt {attempt}): {str(exception)}")
            next_delay = retry_config.calculate_delay(attempt - 1)
            print(f"   Retrying in {next_delay:.1f}s (attempt {attempt + 1})...")

        provider = LLMProvider.ANTHROPIC if self.config.llm.provider.lower() == "anthropic" else LLMProvider.OPENAI
        self.llm_client = LLMClient(
            api_key=self.config.llm.api_key,
            provider=provider,
            api_base=self.config.llm.api_base,
            model=self.config.llm.model,
            verify=self.config.llm.verify,
            ssl_ca_path=self.config.llm.ssl_ca_path,
            retry_config=retry_config if self.config.llm.retry.enabled else None,
        )
        
        if self.config.llm.retry.enabled:
            self.llm_client.retry_callback = on_retry
        
        self.agent = None
        self._loop = asyncio.get_event_loop()

    async def _init_agent(self):
        """Async initialization of agent and tools"""
        tools, skill_loader = await initialize_base_tools(self.config)
        add_workspace_tools(tools, self.config, self.workspace_dir)
        
        system_prompt = GAIA_SYSTEM_PROMPT
        if skill_loader:
            skills_metadata = skill_loader.get_skills_metadata_prompt()
            system_prompt = system_prompt.replace("{SKILLS_METADATA}", skills_metadata or "")
        else:
            system_prompt = system_prompt.replace("{SKILLS_METADATA}", "")

        self.agent = Agent(
            llm_client=self.llm_client,
            system_prompt=system_prompt,
            tools=tools,
            max_steps=self.config.agent.max_steps,
            workspace_dir=str(self.workspace_dir),
        )

    def run(self, question: str, file_path: str | None = None) -> str:
        """
        Run the agent on a question (Sync wrapper)
        """
        if self.agent is None:
            self._loop.run_until_complete(self._init_agent())
        
        # Reset agent messages for each run to avoid context buildup from previous questions
        self.agent.messages = [self.agent.messages[0]]
        
        full_question = question
        if file_path:
            # GAIA sometimes provides file_path relative to dataset root
            abs_file_path = os.path.abspath(file_path)
            full_question = f"{question}\n\n[File available: {abs_file_path}]"
            
        print(f"\n🚀 Running Mini-Agent on: {question[:100]}...")
        
        self.agent.add_user_message(full_question)
        
        # Print agent basic config
        print(f"\n{'-'*40}")
        print(f"🤖 Agent Configuration:")
        print(f"   Model: {self.config.llm.model}")
        print(f"   Provider: {self.config.llm.provider}")
        print(f"   API Base: {self.config.llm.api_base}")
        print(f"   Workspace: {self.workspace_dir}")
        print(f"   Max Steps: {self.config.agent.max_steps}")
        print(f"{'-'*40}")
        
        response = self._loop.run_until_complete(self.agent.run())
        
        # Extract FINAL ANSWER
        return self._extract_final_answer(response)

    def _extract_final_answer(self, response: str) -> str:
        """Extract the FINAL ANSWER from the agent's response"""
        final_answer_pattern = r'FINAL ANSWER:\s*(.+?)(?:\n|$)'
        match = re.search(final_answer_pattern, response, re.IGNORECASE | re.MULTILINE)
        if match:
            answer = match.group(1).strip()
            return answer.strip('[]')
        
        # Fallback to the last line
        lines = response.strip().split('\n')
        if lines:
            return lines[-1].strip()
        return response.strip()

def evaluate_gaia_with_mini_agent(level=1, max_samples=5, data_dir=None):
    """Run GAIA evaluation"""
    from evaluation.tools import GAIAEvaluationTool
    
    wrapper = MiniAgentGAIAWrapper()
    gaia_tool = GAIAEvaluationTool(data_dir=data_dir)
    
    results = gaia_tool.run(
        agent=wrapper,
        level=level,
        max_samples=max_samples,
        export_results=True,
        generate_report=True
    )
    
    return results

if __name__ == "__main__":
    # Configure these paths as needed
    GAIA_DATA_DIR = "dataset_gaia"
    
    # Run evaluation for Level 1
    results = evaluate_gaia_with_mini_agent(
        level=1, 
        max_samples=5, 
        data_dir=GAIA_DATA_DIR
    )
    
    print("\n" + "="*60)
    print("GAIA Evaluation Summary")
    print("="*60)
    print(f"Level 1 Exact Match Rate: {results['exact_match_rate']:.2%}")
    print(f"Total Samples: {results['total_samples']}")
    print("="*60)
