# utils.py
"""
Utility functions for the agent
"""

import logging
from typing import Any

logger = logging.getLogger("superagent")


def print_execution_log(result):
    """Print execution log to console and log file"""
    print("\n" + "="*50)
    print("🚀 EXECUTION FLOW LOG")
    print("="*50 + "\n")
    
    logger.info("="*50)
    logger.info("🚀 EXECUTION FLOW LOG")
    logger.info("="*50)

    for i, msg in enumerate(result["messages"]):
        # -------------------------------------------------
        # 1. User Message (Human Message)
        # -------------------------------------------------
        if msg.type == "human":
            print(f"👤 [User]: {msg.content}")
            logger.info(f"[User]: {msg.content}")
            print("-" * 50)
            logger.info("-" * 50)

        # -------------------------------------------------
        # 2. AI Message (AI Message)
        # -------------------------------------------------
        elif msg.type == "ai":
            # A. Check for hidden thoughts (Sanitized Model stored)
            thought = msg.additional_kwargs.get("thought_process")
            if thought:
                print(f"🧠 [AI Thought]: (Hidden, {len(thought)} chars)...")
                logger.info(f"[AI Thought]: (Hidden, {len(thought)} chars)...")
            
            # B. Check for text response (Content)
            if msg.content:
                print(f"🤖 [AI Says]: {msg.content}")
                logger.info(f"[AI Says]: {msg.content}")

            # C. Check for tool calls (Tool Calls)
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_name = tc['name']
                    tool_args = tc['args']
                    
                    print(f"🛠️  [AI Calls Tool]: {tool_name}, {tool_args}")
                    logger.info(f"[AI Calls Tool]: {tool_name}, {tool_args}")
                    
                    # Special handling: if write_todos, print the plan clearly
                    if tool_name == "write_todos":
                        todos = tool_args.get('todos', [])
                        print("    📋 Current Plan:")
                        logger.info("📋 Current Plan:")
                        for idx, todo in enumerate(todos):
                            status_icon = "✅" if todo.get('status') == 'done' else "⏳"
                            print(f"       {idx+1}. {status_icon} {todo.get('content')}")
                            logger.info(f"{idx+1}. {status_icon} {todo.get('content')}")

            print("-" * 50)
            logger.info("-" * 50)

        # -------------------------------------------------
        # 3. Tool Result (Tool Message)
        # -------------------------------------------------
        elif msg.type == "tool":
            tool_name = msg.name if hasattr(msg, 'name') else "Tool"
            content = str(msg.content)
            
            # If output is too long (e.g., ls hundreds of files, or read_file), truncate
            preview = content.replace('\n', ' ')
            print(f"📦 [Tool Output]: {preview}")
            logger.info(f"[Tool Output]: {preview}")
            
            print("-" * 50)
            logger.info("-" * 50)

    print("\n✅ Execution Finished.")
    logger.info("✅ Execution Finished.")
