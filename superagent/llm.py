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


def build_qwen_llm() -> ChatOpenAI:
    """Builds the Qwen instance using the custom class."""
    CERTFILE = Path(__file__).parent / "ollama-api-fullchain_dgx.pem"
    ssl_context = ssl.create_default_context(cafile=str(CERTFILE)) if CERTFILE.exists() else None
    os.environ["no_proxy"] = "ollama-api.tech.emea.porsche.biz"

    # Instantiate our subclass directly
    return ChatOpenAI(
        api_key="dummy-key",
        base_url="https://ollama-api.tech.emea.porsche.biz/v1",
        model="qwen3:235b",
        temperature=0, 
        max_tokens=65536,
        http_client=httpx.Client(verify=ssl_context, timeout=60.0) if ssl_context else httpx.Client(timeout=60.0),
        http_async_client=httpx.AsyncClient(verify=ssl_context, timeout=60.0) if ssl_context else httpx.AsyncClient(timeout=60.0),
        streaming=False
    )

def build_qwenvl_llm() -> ChatOpenAI:
    """Builds the Qwen instance using the custom class."""
    CERTFILE = Path(__file__).parent / "ollama-api-fullchain_dgx.pem"
    ssl_context = ssl.create_default_context(cafile=str(CERTFILE)) if CERTFILE.exists() else None
    os.environ["no_proxy"] = "ollama-api.tech.emea.porsche.biz"

    # Instantiate our subclass directly
    return ChatOpenAI(
        api_key="dummy-key",
        base_url="https://ollama-api.tech.emea.porsche.biz/v1",
        model="qwen3-vl:235b",
        temperature=0, 
        max_tokens=65536,
        http_client=httpx.Client(verify=ssl_context, timeout=60.0) if ssl_context else httpx.Client(timeout=60.0),
        http_async_client=httpx.AsyncClient(verify=ssl_context, timeout=60.0) if ssl_context else httpx.AsyncClient(timeout=60.0),
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


def build_qwenvl32b_llm() -> ChatOpenAI:

    return ChatOpenAI(
        api_key="dummy-key",
        base_url="https://prodphmjps001sha.tech.emea.porsche.biz:8000/v1",
        model="cpatonn-mirror/Qwen3-VL-32B-Thinking-AWQ-4bit",
        temperature=0,
        max_tokens=8192,
        http_client=httpx.Client(verify=False),
        streaming=False
    )
 

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