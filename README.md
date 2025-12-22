# SuperAgent 🚀

> **The most extensible AI agent framework for complex task automation**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-✅-green.svg)](https://langchain-ai.github.io/langgraph/)
[![DeepAgents](https://img.shields.io/badge/DeepAgents-✅-orange.svg)](https://github.com/langchain-ai/deepagents)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SuperAgent** is a powerful, extensible AI agent framework built on top of LangGraph and DeepAgents. It provides a clean architecture for creating sophisticated AI agents that can handle complex tasks with middleware, subagents, and customizable prompts.

## ✨ Features

- 🏗️ **Extensible Architecture**: Designed as a library for easy extension
- 🔌 **Multi-LLM Support**: Built-in support for Qwen and Gemini models
- 🛠️ **Middleware System**: Extend agent capabilities with custom middleware
- 🤖 **Subagent Support**: Delegate complex tasks to specialized subagents
- 📝 **Customizable Prompts**: Easy prompt management and customization
- 🔧 **Tool Management**: Human-in-the-loop approval for sensitive operations
- 📊 **Comprehensive Logging**: Detailed execution logs for debugging
- 🧠 **Long-term Memory**: Hierarchical memory system with user and project memory
- 🚀 **Production Ready**: Clean codebase following best practices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [UV](https://github.com/astral-sh/uv) (not ready) or virtualenv

### Local Model Setup (Optional)

If you plan to use local models (like Qwen on DGX), you need to copy the SSL certificate file:

```bash
# Copy the SSL certificate for local model access
cp /path/to/your/certificate.pem superagent/ollama-api-fullchain_dgx.pem
```

**Note**: The certificate file is excluded from version control for security reasons. You must manually copy it to the `superagent/` directory if you need to use local models.

### Installation

#### Option 1: Using UV (Recommended)

```bash
# Install UV if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup the project
cd superagent
uv sync
uv run python main.py
```

#### Option 2: Using Virtualenv

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run the agent
python main.py
```

## 📖 Usage

### Basic Agent Creation

```python
from superagent import create_simple_agent, llm_dgx

# Create a simple agent
agent = create_simple_agent(
    model=llm_dgx,
    working_dir="/path/to/your/project",
    auto_approve=True,  # Auto-approve tool calls
    enable_subagents=True  # Enable subagent functionality
)

# Run the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Your task here"}]
})
```

### Advanced Configuration

```python
from superagent import create_superagent, build_gemini_llm

# Create a fully customized agent
agent, backend = create_superagent(
    model=build_gemini_llm(),  # Use Gemini model
    working_dir="/path/to/project",
    tools=[your_custom_tools],  # Add custom tools
    system_prompt="Your custom system prompt",
    auto_approve=False,  # Manual approval for sensitive operations
    enable_subagents=True
)
```

## 🧠 Memory Module

### Memory System Architecture

SuperAgent's memory system uses a **hierarchical storage architecture** based on deepagents-cli design principles, enabling persistent long-term memory functionality.

#### Core Design Principles

1. **Hierarchical Memory Storage**
   - **User Memory**: Stored in `~/.superagent/{agent}/`, applicable to all projects
   - **Project Memory**: Stored in the project root directory, specific to the current project

2. **Memory-First Response Pattern**
   - Check project memory before answering any questions
   - If project memory is insufficient, check user memory
   - Supplement general knowledge with saved knowledge

3. **Dynamic Memory Updates**
   - Immediately update memory when users describe roles or behaviors
   - Update memory based on user feedback to improve performance
   - Capture pattern preferences and workflows for continuous learning

#### Memory File Structure

```
# User Memory (Global)
~/.superagent/superagent/
├── agent.md              # User preferences and general behavior
└── other_memory_files.md # Other user memory files

# Project Memory (Project-specific)
[project-root]/
├── .superagent/
│   ├── agent.md          # Project-specific instructions (preferred location)
│   └── api-design.md     # Project-specific reference documentation
└── agent.md              # Project memory (fallback location)
```

#### System Prompt Injection

The memory system automatically injects memory content into the system prompt through middleware:

```python
# System prompt structure
<user_memory>
{user_memory_content}
</user_memory>

<project_memory>
{project_memory_content}
</project_memory>

{base_system_prompt}

## Long-term Memory Documentation
{detailed_memory_usage_instructions}
```

### Usage Scenarios

1. **At session start**: Automatically check user and project memory
2. **Before answering questions**: Prioritize project memory, then user memory
3. **When receiving user feedback**: Immediately update relevant memory files
4. **Pattern recognition**: Capture workflow preferences and encode as memory patterns

## 🔌 LLM Provider Integration

### Adding New LLM Providers

SuperAgent is designed to be easily extensible with new LLM providers. Here's how to add support for additional LLM services:

#### 1. Basic LLM Provider Template

Create a new function in `superagent/llm.py` following this pattern:

```python
from langchain_openai import ChatOpenAI
import httpx
import ssl
from pathlib import Path

def build_custom_llm() -> ChatOpenAI:
    """Build custom LLM instance"""
    
    # Configuration for your LLM provider
    api_key = "your-api-key"  # Use environment variables for security
    base_url = "https://api.your-llm-provider.com/v1"
    model_name = "your-model-name"
    
    # Optional: SSL configuration for self-signed certificates
    cert_file = Path(__file__).parent / "your-certificate.pem"
    ssl_context = ssl.create_default_context(cafile=str(cert_file)) if cert_file.exists() else None
    
    # Create the LLM instance
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=0,  # Adjust as needed
        max_tokens=32768,  # Adjust based on model limits
        http_client=httpx.Client(verify=ssl_context) if ssl_context else None
    )
    
    return llm

# Export the LLM instance
llm_custom = build_custom_llm()
```

#### 2. Environment Variables (Recommended)

For security, use environment variables instead of hardcoded values:

```python
import os

def build_custom_llm() -> ChatOpenAI:
    """Build custom LLM instance using environment variables"""
    
    api_key = os.getenv("CUSTOM_LLM_API_KEY")
    base_url = os.getenv("CUSTOM_LLM_BASE_URL", "https://api.your-llm-provider.com/v1")
    model_name = os.getenv("CUSTOM_LLM_MODEL", "your-default-model")
    
    if not api_key:
        raise ValueError("CUSTOM_LLM_API_KEY environment variable is required")
    
    # Rest of the configuration...
```

#### 3. Provider-Specific Examples

**OpenAI Integration:**

```python
def build_openai_llm() -> ChatOpenAI:
    """Build OpenAI model instance"""
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o",
        temperature=0,
        max_tokens=16384
    )

llm_openai = build_openai_llm()
```

**Anthropic Integration:**

```python
from langchain_anthropic import ChatAnthropic

def build_anthropic_llm() -> ChatAnthropic:
    """Build Anthropic Claude model instance"""
    return ChatAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",
        temperature=0,
        max_tokens=4096
    )

llm_anthropic = build_anthropic_llm()
```

**Local Ollama Integration:**

```python
def build_ollama_llm() -> ChatOpenAI:
    """Build local Ollama model instance"""
    return ChatOpenAI(
        api_key="ollama",  # Dummy key for Ollama
        base_url="http://localhost:11434/v1",
        model="llama3.1:8b",
        temperature=0,
        max_tokens=32768
    )

llm_ollama = build_ollama_llm()
```

#### 4. Update Exports

Add your new LLM instances to `superagent/__init__.py`:

```python
# In superagent/__init__.py
from .llm import (
    llm_dgx,
    llm_qwen,
    llm_gemini,
    llm_custom,  # Add your new LLM
    build_qwen_llm,
    build_gemini_llm,
    build_custom_llm,  # Add your builder function
)

__all__ = [
    # ... existing exports
    "llm_custom",
    "build_custom_llm",
]
```

#### 5. Usage in Your Application

```python
from superagent import create_simple_agent, llm_custom

# Use your custom LLM
agent = create_simple_agent(
    model=llm_custom,
    working_dir=".",
    auto_approve=True
)
```

### Configuration Tips

- **Model Selection**: Choose models based on your task requirements (reasoning, coding, analysis)
- **Token Limits**: Set appropriate max_tokens based on model capabilities
- **Temperature**: Use temperature=0 for deterministic tasks, higher for creative tasks
- **Error Handling**: Implement proper error handling for API failures
- **Rate Limiting**: Add rate limiting for production use

## 🏗️ Architecture

### Project Structure

```
superagent/
├── superagent/           # Core package
│   ├── __init__.py      # Public API exports
│   ├── agent.py         # Agent creation and management
│   ├── agent_memory.py  # Memory system implementation
│   ├── llm.py           # LLM configuration and models
│   ├── prompt.py        # Prompt management
│   ├── config.py        # Configuration settings
│   └── utils.py         # Utility functions
├── main.py              # CLI entry point
├── pyproject.toml       # Project configuration
├── setup.py            # Package setup
└── README.md           # This file
```

### Core Components

1. **Agent Management** (`agent.py`): Core agent creation and lifecycle management
2. **Memory System** (`agent_memory.py`): Hierarchical long-term memory with middleware
3. **LLM Configuration** (`llm.py`): Multi-model support (Qwen, Gemini)
4. **Prompt System** (`prompt.py`): Flexible prompt management
5. **Utilities** (`utils.py`): Logging and execution tracking

## 🔧 Development Guide

### Building Custom Agents

#### 1. Basic Agent Setup

```python
from superagent import create_simple_agent

# Minimal agent setup
agent = create_simple_agent(
    model="qwen",  # or "gemini"
    working_dir=".",
    auto_approve=True
)
```

#### 2. Custom Prompt Configuration

Edit `superagent/prompt.py` to modify the system prompt:

```python
def get_custom_agent_prompt() -> str:
    """Your custom system prompt"""
    return """
You are a specialized AI assistant for [your domain].

# Your custom instructions here...
"""

# Update the default prompt function
def get_default_agent_prompt() -> str:
    return get_custom_agent_prompt()
```

#### 3. Adding Custom Tools

```python
from langchain.tools import tool

@tool
def custom_tool(parameter: str) -> str:
    """Description of your custom tool"""
    return f"Processed: {parameter}"

# Use in agent creation
agent = create_superagent(
    model=llm_dgx,
    tools=[custom_tool],  # Add your custom tools
    # ... other parameters
)
```

## 🚧 TODO List

### High Priority
- [ ] **Middleware System**: Implement extensible middleware architecture
- [ ] **Subagent Framework**: Complete subagent delegation system
- [ ] **Schema Validation**: Add input/output schema validation
- [ ] **Configuration Management**: Enhanced config system with environment variables

### Medium Priority
- [ ] **More LLM Providers**: Add support for OpenAI, Anthropic, etc.
- [ ] **Plugin System**: Develop plugin architecture for easy extensions
- [ ] **Testing Suite**: Comprehensive test coverage
- [ ] **Documentation**: API documentation and examples

### Low Priority
- [ ] **Web Interface**: Optional web-based agent interface
- [ ] **Performance Optimization**: Caching and optimization
- [ ] **Monitoring**: Advanced monitoring and metrics
- [ ] **Deployment Tools**: Docker and cloud deployment support

## 🔌 Extending SuperAgent

### Adding Middleware (TODO)

```python
# Planned middleware interface
class CustomMiddleware:
    def pre_process(self, input_data):
        # Pre-processing logic
        return input_data
    
    def post_process(self, output_data):
        # Post-processing logic
        return output_data
```

### Creating Subagents (TODO)

```python
# Planned subagent system
class SpecializedSubagent:
    def __init__(self, specialization):
        self.specialization = specialization
    
    def handle_task(self, task_description):
        # Subagent task handling logic
        return result
```

## 🔄 Integration Guide - How to Use SuperAgent Library

### 1. llm.py Integration Modifications

In your existing llm.py file, add SuperAgent library imports and model configuration:

```python
# Add imports at the top of your llm.py file
from superagent.llm import build_qwen_llm, build_gemini_llm, get_llm

# If you have existing local model configurations, add compatibility functions
def get_superagent_llm(model_type="qwen", enable_memory=True):
    """Get SuperAgent-compatible LLM instance"""
    llm = get_llm(model_type)
    
    # Configure memory functionality if needed
    if enable_memory:
        # Memory functionality is integrated in agent creation functions
        pass
        
    return llm

# Keep existing functions and add SuperAgent compatibility
def create_agent_with_memory(model_type="qwen", working_dir=".", assistant_id="superagent"):
    """Create agent with memory functionality"""
    from superagent import create_simple_agent
    
    llm = get_llm(model_type)
    agent = create_simple_agent(
        model=llm,
        working_dir=working_dir,
        auto_approve=True,
        enable_subagents=True,
        enable_memory=True,  # Enable memory functionality
        assistant_id=assistant_id
    )
    return agent
```

### 2. main.py Integration Modifications

In your main.py file, modify the root_path and input_text configurations:

```python
# Modify root_path to your project path
root_path = "/path/to/your/project"  # Change to actual project path

# Modify input_text with specific task description
input_text = """
Please analyze the code structure of the current project and generate project documentation.
Focus on analyzing:
1. Project architecture and module division
2. Main functional modules
3. Dependencies
4. Configuration file descriptions
"""

# Create agent with memory functionality
agent = create_simple_agent(
    model=llm_dgx,
    working_dir=root_path,
    auto_approve=True,
    enable_subagents=True,
    enable_memory=True,  # Enable memory functionality
    assistant_id="documentation_agent"  # Set different IDs for different agent purposes
)

# Run the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": input_text}]
})
```

### 3. Memory File Configuration

#### User Memory Configuration (~/.superagent/superagent/agent.md)

```markdown
# User Preferences and General Behavior

## General Instructions
- Use English for communication
- Use English for code comments
- Prioritize clear and concise expression
- For complex tasks, create a plan first then execute

## Coding Standards
- Python code follows PEP8 standards
- Use type annotations
- Functions and classes should have clear docstrings
- Implement proper error handling

## Workflow
- Analyze task requirements first
- Create detailed execution plan
- Execute step by step and verify results
- Generate comprehensive execution report
```

#### Project Memory Configuration ([project-root]/.superagent/agent.md)

```markdown
# Project-Specific Instructions

## Project Overview
Project Name: [Project Name]
Project Type: [Project Type, e.g., Web Application, Data Analysis, etc.]
Technology Stack: [Technology frameworks and tools used]

## Project Standards
- Code Organization: [Describe project directory structure]
- Naming Conventions: [Variable, function, class naming rules]
- Documentation Requirements: [Documentation format and content requirements]
- Testing Requirements: [Test coverage and testing methods]

## Specific Workflows
- Deployment Process: [Deployment steps and considerations]
- Debugging Methods: [Common issue troubleshooting methods]
- Performance Optimization: [Performance optimization suggestions]
```

### 4. Dependency Management

Add dependencies to your project's requirements.txt or pyproject.toml:

```toml
# pyproject.toml
[project]
dependencies = [
    "superagent>=1.0.0",
    # Other dependencies...
]

# Or install via git
pip install git+https://github.com/your-username/superagent.git
```

### 5. Configuration Example

Complete main.py configuration example:

```python
#!/usr/bin/env python3
import logging
from pathlib import Path
from superagent import create_simple_agent, llm_dgx

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    # Project root path
    root_path = "/home/lihan/project/your-project"
    
    # Task description
    input_text = """
    Please analyze the code structure of the current project, focusing on:
    1. Main modules and functions
    2. Dependency graph
    3. Configuration file descriptions
    4. Deployment process
    
    Please generate a detailed documentation report.
    """
    
    # Create agent with memory functionality
    agent = create_simple_agent(
        model=llm_dgx,
        working_dir=root_path,
        auto_approve=True,
        enable_subagents=True,
        enable_memory=True,
        assistant_id="analysis_agent"
    )
    
    # Execute task
    result = agent.invoke({
        "messages": [{"role": "user", "content": input_text}]
    })
    
    print("Task completed!")

if __name__ == "__main__":
    main()
```

With the above configuration, you can easily integrate the SuperAgent library into your existing projects and fully utilize its memory functionality to improve agent performance and consistency.

## 🐛 Troubleshooting

### Common Issues

**SSL Certificate Errors:**
```bash
# Ensure certificate file exists
ls -la superagent/superagent/ollama-api-fullchain_dgx.pem
```

**Import Errors:**
```bash
# Make sure you're in the correct directory
cd /home/lihan/project/llm_application/superagent
uv run python main.py
```

**Model Connection Issues:**
- Check your network connection
- Verify API keys and endpoints
- Ensure required environment variables are set

### Debug Mode

Enable detailed logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    # ... other config
)
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines (TODO) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Write docstrings for all public functions
- Keep functions focused and single-purpose

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [LangGraph](https://github.com/langchain-ai/langgraph)
- Inspired by [DeepAgents](https://github.com/langchain-ai/deepagents)
- Uses [Qwen](https://github.com/QwenLM/Qwen) and [Gemini](https://ai.google.dev/) models

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/superagent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/superagent/discussions)
- **Email**: support@your-org.com

---

<div align="center">

**Made with ❤️ by the SuperAgent Team**

[![Star History Chart](https://api.star-history.com/svg?repos=your-org/superagent&type=Date)](https://star-history.com/#your-org/superagent&Date)

</div>