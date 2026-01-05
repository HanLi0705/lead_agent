"""
GAIA Evaluation Example

This example demonstrates how to use the GAIA evaluation tool to evaluate a superagent.
"""

import os
import re
import sys
from pathlib import Path

# Add parent directory to Python path to import superagent module
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
sys.path.insert(0, str(parent_dir))

from superagent import create_simple_agent
from superagent.llm import get_llm

# GAIA official system prompt (from paper) with enhanced tool usage instructions
GAIA_SYSTEM_PROMPT = """You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].

YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.

If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.

If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.

If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."""



class SuperAgentWrapper:
    """Wrapper for superagent to make it compatible with GAIA evaluation tool"""
    
    def __init__(self, 
                 working_dir: str | None = None,
                 auto_approve: bool = False):
        """
        Initialize superagent wrapper
        
        Args:
            working_dir: Working directory for file operations (should be GAIA dataset directory)
            auto_approve: Whether to auto-approve all tool calls
        """
        # Use build_qwen_llm to get the Qwen model
        self.model = get_llm()
        self.working_dir = working_dir or str(Path.cwd())
        self.auto_approve = auto_approve
        self.current_file_path = None
        
        # Create superagent with GAIA system prompt
        self.agent = create_simple_agent(
            model=self.model,
            working_dir=self.working_dir,
            auto_approve=auto_approve,
            enable_subagents=True,
            enable_memory=True,
        )
    
    def run(self, question: str, file_path: str | None = None) -> str:
        """
        Run the agent on a question
        
        Args:
            question: The question to answer
            file_path: Optional path to a file that should be referenced in the question
            
        Returns:
            Agent's response (extracted FINAL ANSWER)
        """
        import json
        import re
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
        
        # Generate a unique thread_id for each question
        import uuid
        thread_id = str(uuid.uuid4())
        
        # Build the full question with file information if provided
        full_question = question
        if file_path:
            # Construct absolute path to the file
            if not os.path.isabs(file_path):
                abs_file_path = os.path.join(self.working_dir, file_path)
            else:
                abs_file_path = file_path
            
            # Add file information to the question
            full_question = f"{question}\n\n[File available: {abs_file_path}]"
        
        # Log agent invocation
        print("\n" + "="*80)
        print("🤖 AGENT INVOCATION LOG")
        print("="*80)
        print(f"\n📅 Thread ID: {thread_id}")
        print(f"\n📥 INPUT MESSAGE:")
        print(f"   Role: system")
        print(f"   Content: {GAIA_SYSTEM_PROMPT[:200]}...")
        print(f"\n📥 INPUT MESSAGE:")
        print(f"   Role: user")
        print(f"   Content: {full_question}")
        print(f"\n🔧 Working Directory: {self.working_dir}")
        print(f"🔧 Auto Approve: {self.auto_approve}")
        if file_path:
            print(f"📎 File Path: {file_path}")
        
        # Invoke the agent with the question
        result = self.agent.invoke({
            "messages": [
                {"role": "system", "content": GAIA_SYSTEM_PROMPT},
                {"role": "user", "content": full_question}
            ]
        }, config={"configurable": {"thread_id": thread_id}})
        
        # Log all messages from the agent
        print(f"\n📤 OUTPUT MESSAGES:")
        messages = result.get("messages", [])
        
        agent_raw_response = ""
        for i, msg in enumerate(messages):
            print(f"\n   [Message {i+1}]")
            
            if isinstance(msg, AIMessage):
                print(f"   Type: AIMessage")
                print(f"   Content: {msg.content}")
                agent_raw_response = msg.content
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    print(f"   Tool Calls: {len(msg.tool_calls)}")
                    for j, tool_call in enumerate(msg.tool_calls):
                        print(f"      [{j+1}] {tool_call.get('name', 'unknown')}")
                        print(f"          Args: {tool_call.get('args', {})}")
                if hasattr(msg, 'response_metadata'):
                    print(f"   Response Metadata: {msg.response_metadata}")
                    
            elif isinstance(msg, HumanMessage):
                print(f"   Type: HumanMessage")
                print(f"   Content: {msg.content}")
                
            elif isinstance(msg, SystemMessage):
                print(f"   Type: SystemMessage")
                print(f"   Content: {msg.content}")
                
            elif isinstance(msg, ToolMessage):
                print(f"   Type: ToolMessage")
                print(f"   Tool Call ID: {msg.tool_call_id}")
                print(f"   Content: {msg.content[:200]}..." if len(msg.content) > 200 else f"   Content: {msg.content}")
                
            elif isinstance(msg, dict):
                print(f"   Type: dict")
                print(f"   Role: {msg.get('role', 'unknown')}")
                content = msg.get('content', '')
                print(f"   Content: {content[:200]}..." if len(content) > 200 else f"   Content: {content}")
                if msg.get("role") == "assistant":
                    agent_raw_response = content
                if 'tool_calls' in msg:
                    print(f"   Tool Calls: {msg['tool_calls']}")
            else:
                print(f"   Type: {type(msg).__name__}")
                print(f"   Content: {str(msg)[:200]}...")
        
        # Extract FINAL ANSWER according to GAIA format
        final_answer = self._extract_final_answer(agent_raw_response)
        
        print(f"\n✅ FINAL RESPONSE:")
        print(f"   Raw: {agent_raw_response[:200]}...")
        print(f"   Extracted FINAL ANSWER: {final_answer}")
        print("="*80 + "\n")
        
        return final_answer
    
    def _extract_final_answer(self, response: str) -> str:
        """
        Extract the FINAL ANSWER from the agent's response according to GAIA format
        
        GAIA requires answers in format: FINAL ANSWER: [YOUR FINAL ANSWER]
        
        Args:
            response: Raw agent response
            
        Returns:
            Extracted final answer
        """
        # First try to extract GAIA official format
        final_answer_pattern = r'FINAL ANSWER:\s*(.+?)(?:\n|$)'
        match = re.search(final_answer_pattern, response, re.IGNORECASE | re.MULTILINE)
        if match:
            answer = match.group(1).strip()
            # Remove possible square brackets
            answer = answer.strip('[]')
            # Handle LaTeX format: \boxed{...}
            boxed_match = re.search(r'\\boxed\{([^}]+)\}', answer)
            if boxed_match:
                answer = boxed_match.group(1)
                # Handle fractions: \frac{a}{b} -> a/b
                frac_match = re.search(r'\\frac\{([^}]+)\}\{([^}]+)\}', answer)
                if frac_match:
                    numerator = frac_match.group(1)
                    denominator = frac_match.group(2)
                    # Try to evaluate the fraction
                    try:
                        from fractions import Fraction
                        value = Fraction(numerator) / Fraction(denominator)
                        answer = str(value)
                    except:
                        answer = f"{numerator}/{denominator}"
            return answer
        
        # Fallback patterns
        answer_patterns = [
            r'答案[：:]\s*(.+)',
            r'最终答案[：:]\s*(.+)',
            r'Final answer[：:]\s*(.+)',
            r'Answer[：:]\s*(.+)',
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                # Handle LaTeX format
                boxed_match = re.search(r'\\boxed\{([^}]+)\}', answer)
                if boxed_match:
                    answer = boxed_match.group(1)
                    # Handle fractions
                    frac_match = re.search(r'\\frac\{([^}]+)\}\{([^}]+)\}', answer)
                    if frac_match:
                        numerator = frac_match.group(1)
                        denominator = frac_match.group(2)
                        try:
                            from fractions import Fraction
                            value = Fraction(numerator) / Fraction(denominator)
                            answer = str(value)
                        except:
                            answer = f"{numerator}/{denominator}"
                return answer
        
        # If no patterns found, return the last non-empty line
        lines = response.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle LaTeX format
                boxed_match = re.search(r'\\boxed\{([^}]+)\}', line)
                if boxed_match:
                    answer = boxed_match.group(1)
                    # Handle fractions
                    frac_match = re.search(r'\\frac\{([^}]+)\}\{([^}]+)\}', answer)
                    if frac_match:
                        numerator = frac_match.group(1)
                        denominator = frac_match.group(2)
                        try:
                            from fractions import Fraction
                            value = Fraction(numerator) / Fraction(denominator)
                            answer = str(value)
                        except:
                            answer = f"{numerator}/{denominator}"
                    return answer
                return line
        
        return response.strip()


def evaluate_gaia_with_agent(agent, level=1, max_samples=5, data_dir=None, subset="validation"):
    """
    Evaluate an agent on GAIA benchmark
    
    Args:
        agent: Agent instance with a run() method
        level: GAIA difficulty level (1, 2, or 3)
        max_samples: Maximum number of samples to evaluate
        data_dir: Path to the GAIA dataset directory
        subset: Dataset subset (test or validation)
        
    Returns:
        Evaluation results dictionary
    """
    from evaluation.tools import GAIAEvaluationTool
    
    # 创建GAIA评估工具
    gaia_tool = GAIAEvaluationTool(data_dir=data_dir)
    
    # 运行评估
    results = gaia_tool.run(
        agent=agent,
        level=level,
        max_samples=max_samples,
        export_results=True,
        generate_report=True
    )
    
    # 查看结果
    print(f"exact match: {results['exact_match_rate']:.2%}")
    print(f"partial match: {results['partial_match_rate']:.2%}")
    print(f"exact match rate: {results['exact_matches']}/{results['total_samples']}")
    
    return results


# Example usage with superagent
if __name__ == "__main__":
    # Create superagent wrapper
    # working_dir should be the GAIA dataset directory where you downloaded the data
    # This is typically the path returned by download_gaia.py
    agent = SuperAgentWrapper(
        working_dir="/home/lihan/project/llm_application/han/dataset_gaia",  # GAIA数据集目录
        auto_approve=False  # Set to True to auto-approve all tool calls
    )
    
    # Test different difficulty levels
    levels_to_test = [1, 2, 3]
    max_samples_per_level = 1
    
    all_results = {}
    
    for level in levels_to_test:
        print(f"\n{'='*80}")
        print(f"Testing Level {level}")
        print(f"{'='*80}\n")
        
        # Evaluate on GAIA
        results = evaluate_gaia_with_agent(
            agent, 
            level=level, 
            max_samples=max_samples_per_level,
            data_dir="/home/lihan/project/llm_application/han/dataset_gaia"  # 传递数据集目录
        )
        
        all_results[f"level_{level}"] = results
    
    # Print summary across all levels
    print("\n" + "="*80)
    print("SUMMARY ACROSS ALL LEVELS")
    print("="*80)
    
    for level_key, results in all_results.items():
        level_num = level_key.split('_')[1]
        print(f"\nLevel {level_num}:")
        print(f"  Exact Match Rate: {results['exact_match_rate']:.2%}")
        print(f"  Partial Match Rate: {results['partial_match_rate']:.2%}")
        print(f"  Exact Matches: {results['exact_matches']}/{results['total_samples']}")
    
    print("\n" + "="*60)
    print("Evaluation completed!")
    print("="*60)
