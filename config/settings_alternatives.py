"""
Configurações alternativas e fallback para LLMs.
"""

import os
import streamlit as st
from typing import Dict, Any, List

def get_api_key(key_name: str = 'OPENROUTER_API_KEY', default: str = '') -> str:
    """Obtém a API key dos secrets do Streamlit ou de variável de ambiente."""
    # Tentar obter dos secrets do Streamlit primeiro (produção)
    try:
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    
    # Fallback para variável de ambiente (desenvolvimento local)
    return os.getenv(key_name, default)

class AlternativeSettings:
    """Configurações de fallback para quando o modelo principal atinge rate limit."""
    
    @staticmethod
    def get_fallback_configs() -> List[Dict[str, Any]]:
        """Retorna configurações de fallback com API keys dos secrets."""
        return [
            {
                # Opção 1: xAI Grok 4 Fast (2M contexto, gratuito) - TESTANDO PRIMEIRO
                "name": "xAI Grok 4 Fast",
                "config": {
                    "model_name": "x-ai/grok-4-fast:free",
                    "base_url": "https://openrouter.ai/api/v1",
                    "api_key": get_api_key("OPENROUTER_API_KEY"),
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "rate_limit": 100,  # estimado por dia
                "is_free": True,
                "context_length": "2M tokens"
            },
            {
                # Opção 2: Meta Llama 3.2 3B via OpenRouter (gratuito)
                "name": "Meta Llama 3.2 3B",
                "config": {
                    "model_name": "meta-llama/llama-3.2-3b-instruct:free",
                    "base_url": "https://openrouter.ai/api/v1",
                    "api_key": get_api_key("OPENROUTER_API_KEY"),
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "rate_limit": 200,  # estimado por dia
                "is_free": True,
                "context_length": "128k tokens"
            },
            {
                # Opção 3: DeepSeek Free (movido para cima - funciona bem)
                "name": "DeepSeek Free",
                "config": {
                    "model_name": "deepseek/deepseek-chat-v3.1:free",
                    "base_url": "https://openrouter.ai/api/v1",
                    "api_key": get_api_key("OPENROUTER_API_KEY"),
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "rate_limit": 50,  # por dia
                "is_free": True,
                "context_length": "256k tokens"
            },
            {
                # Opção 4: OpenAI GPT-3.5 (requer API key)
                "name": "OpenAI GPT-3.5",
                "config": {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": get_api_key("OPENAI_API_KEY", ""),
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "rate_limit": None,
                "is_free": False,
                "requires_key": True
            },
            {
                # Opção 5: Groq Llama (gratuito com rate limit maior)
                "name": "Groq Llama",
                "config": {
                    "model_name": "llama-3.1-8b-instant",
                    "base_url": "https://api.groq.com/openai/v1",
                    "api_key": get_api_key("GROQ_API_KEY", ""),
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "rate_limit": 300,  # por dia (estimado)
                "is_free": True,
                "requires_key": True
            },
            {
                # Opção 6: Google Gemini (gratuito com API key)
                "name": "Google Gemini",
                "config": {
                    "model_name": "gemini-pro",
                    "api_key": get_api_key("GOOGLE_API_KEY", ""),
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "rate_limit": 60,  # por minuto
                "is_free": True,
                "requires_key": True
            }
        ]
    
    # Propriedade para manter compatibilidade
    @property
    def LLM_FALLBACK_CONFIGS(self) -> List[Dict[str, Any]]:
        return self.get_fallback_configs()
    
    # Configuração de cache para reduzir chamadas à API
    CACHE_CONFIG = {
        "enabled": True,
        "ttl": 3600,  # 1 hora em segundos
        "max_size": 100,  # máximo de entradas no cache
        "cache_similar_queries": True  # agrupar queries similares
    }
    
    # Configuração de rate limiting local
    RATE_LIMIT_CONFIG = {
        "enabled": True,
        "requests_per_minute": 10,
        "requests_per_hour": 50,
        "requests_per_day": 200,
        "cooldown_minutes": 5  # tempo de espera após atingir limite
    }

# Instância única
alternative_settings = AlternativeSettings()
