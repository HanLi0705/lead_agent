import ssl
import os
import httpx
import re
from typing import Optional, Any, List, Union
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, AIMessage, AIMessageChunk
from langchain_core.outputs import ChatResult
from pydantic import PrivateAttr

class ResponseCleaningChatOpenAI(ChatOpenAI):
    """
    Inherits directly from ChatOpenAI to preserve all internal attributes 
    (client, model_name, api_base, etc.) while cleaning <think> tags.
    """
    _think_pattern: Any = PrivateAttr()
    _tag_stripper: Any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Regex to match complete <think> blocks, handles unclosed tags at the end
        self._think_pattern = re.compile(r'<(think|thought)>([\s\S]*?)(?:</\1>|$)', re.IGNORECASE)
        # Regex to strip any remaining orphan tags like </think>
        self._tag_stripper = re.compile(r'</?(think|thought)>', re.IGNORECASE)

    @property
    def _llm_type(self) -> str:
        return "response_cleaning_chat_openai"

    def _process_message(self, message: Union[AIMessage, AIMessageChunk]):
        """Extracts reasoning and cleans the content."""
        raw_content = message.content
        if not isinstance(raw_content, str) or not raw_content:
            return

        # 1. Extract reasoning content
        found_thinking = self._think_pattern.findall(raw_content)
        reasoning = "\n".join([t[1].strip() for t in found_thinking])

        # 2. Clean main content
        # Remove complete blocks
        cleaned_content = self._think_pattern.sub('', raw_content)
        # Remove orphan tags
        cleaned_content = self._tag_stripper.sub('', cleaned_content)
        
        # 3. Strip surrounding quotes and whitespace
        # This removes both '...' and "..." that models sometimes add
        cleaned_content = cleaned_content.strip().strip("'").strip('"').strip()

        # 4. Update the message object
        message.content = cleaned_content
        if message.additional_kwargs is None:
            message.additional_kwargs = {}
        message.additional_kwargs["reasoning"] = reasoning

    def _generate(self, *args, **kwargs) -> ChatResult:
        """Intercept sync generation to clean output."""
        result = super()._generate(*args, **kwargs)
        for gen in result.generations:
            if isinstance(gen.message, (AIMessage, AIMessageChunk)):
                self._process_message(gen.message)
        return result

    async def _agenerate(self, *args, **kwargs) -> ChatResult:
        """Intercept async generation to clean output."""
        result = await super()._agenerate(*args, **kwargs)
        for gen in result.generations:
            if isinstance(gen.message, (AIMessage, AIMessageChunk)):
                self._process_message(gen.message)
        return result

def build_qwen_llm() -> ResponseCleaningChatOpenAI:
    """Builds the Qwen instance using the custom class."""
    CERTFILE = Path(__file__).parent / "ollama-api-fullchain_dgx.pem"
    ssl_context = ssl.create_default_context(cafile=str(CERTFILE)) if CERTFILE.exists() else None
    os.environ["no_proxy"] = "ollama-api.tech.emea.porsche.biz"

    # Instantiate our subclass directly
    return ResponseCleaningChatOpenAI(
        api_key="dummy-key",
        base_url="https://ollama-api.tech.emea.porsche.biz/v1",
        model="qwen3:235b",
        temperature=0, 
        max_tokens=65536,
        http_client=httpx.Client(verify=ssl_context, timeout=300.0) if ssl_context else None,
        streaming=False
    )

def build_gemini_llm() -> ChatGoogleGenerativeAI:
    """Builds the Gemini instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", 
        temperature=0,
        max_tokens=128000
    )

def get_llm(model_type: str = "qwen") -> Any:
    """Gets LLM instance based on type."""
    if model_type.lower() == "gemini":
        return build_gemini_llm()
    return build_qwen_llm()

# # Default instances
# llm_qwen = build_qwen_llm()
# llm_dgx = llm_qwen

# --- 测试代码 ---
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    llm = get_llm("qwen")
    res = llm.invoke([HumanMessage(content="1+1等于几？")])
    # 注意：这里直接打印 res.content，不要使用 f"{res.content!r}" 或 repr()
    print(f"Content: {res.content}")
    print(f"Reasoning: {res.additional_kwargs.get('reasoning')}")