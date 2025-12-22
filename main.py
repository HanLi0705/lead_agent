#!/usr/bin/env python3
"""
Main entry point for the superagent CLI
"""

import logging
import sys
from pathlib import Path

# Import from the superagent package
from superagent.agent import create_simple_agent, run_interactive
from superagent.llm import llm_dgx
from superagent.utils import print_execution_log


# Setup logging
# Create logs directory (if it doesn't exist)
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "agent.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("superagent")


def main():
    """Main entry point"""
    # Method 1: Single invocation
    root_path = "/home/lihan/project/llm_application/agents/documentation"
    agent = create_simple_agent(
        model=llm_dgx,
        working_dir=root_path, # Path.cwd(),
        auto_approve=True,  # Requires manual approval for write_file and edit_file
        enable_subagents=True,  # Enable task tool for complex tasks
    )

    # input_text = (
    #     "Find all .svg files in the working directory and save them to an md file"
    # )
    
    # input_text = ("Find A_aab28.svg file in /home/lihan/project/llm_application/agents/documentation folder and analyze its content")
    # input_text = ("Search for stDFCHeatrAvlChk in /home/lihan/project/llm_application/agents/documentation folder")
    input_text = ("this is difficult task.please search stDFCHeatrAvlChk /home/lihan/project/llm_application/agents/documentation,if the results has .svg files, please analyze it, please write the report about how this signal work and what effect this signal, make sure write file to .md file")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": input_text}]},
        config={"configurable": {"thread_id": "default"}}
    )
    # logger.info(f"result: {result}")
    logger.info("\n=== FINAL ANSWER ===")
    print_execution_log(result)
    # Method 2: Interactive run
    # run_interactive(agent)


if __name__ == "__main__":
    main()