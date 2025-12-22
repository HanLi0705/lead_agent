# llm.py
"""
LLM configuration and models
"""

import ssl
import os
import httpx
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from pathlib import Path

def build_qwen_llm() -> ChatOpenAI:
    """Build local Qwen model instance"""
    # SSL configuration
    CERTFILE = Path(__file__).parent / "ollama-api-fullchain_dgx.pem"
    ssl_context = ssl.create_default_context(cafile=str(CERTFILE)) if CERTFILE.exists() else None
    os.environ["no_proxy"] = "ollama-api.tech.emea.porsche.biz"

    # Qwen model instance
    llm = ChatOpenAI(
        api_key="dummy-key",
        base_url="https://ollama-api.tech.emea.porsche.biz/v1",
        model="qwen3-vl:235b",
        temperature=0, 
        max_tokens=65536,
        http_client=httpx.Client(verify=ssl_context)
    )
    return llm


def build_gemini_llm() -> ChatGoogleGenerativeAI:
    """Build Gemini model instance"""
    # Gemini model instance
    llm = ChatGoogleGenerativeAI(  
        model="gemini-3-pro-preview",  
        temperature=0,  
        max_tokens=128000,  
    )  
    return llm


def get_llm(model_type: str = "qwen") -> BaseChatModel:
    """Get LLM instance based on model type
    
    Args:
        model_type: Type of model to use ("qwen" or "gemini")
        
    Returns:
        Configured LLM instance
    """
    if model_type.lower() == "gemini":
        return build_gemini_llm()
    else:
        return build_qwen_llm()


# Default Qwen model instance
llm_qwen = build_qwen_llm()

# Default Gemini model instance  
# llm_gemini = build_gemini_llm()

# Default model (Qwen for backward compatibility)
llm_dgx = llm_qwen
