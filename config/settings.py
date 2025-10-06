"""
Configurações centralizadas da aplicação EDA Agent.
"""

import os
import streamlit as st
from typing import Dict, Any

def get_api_key():
    """Obtém a API key dos secrets do Streamlit ou de variável de ambiente."""
    # Tentar obter dos secrets do Streamlit primeiro (produção)
    try:
        if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
            return st.secrets['OPENROUTER_API_KEY']
    except Exception:
        pass
    
    # Fallback para variável de ambiente (desenvolvimento local)
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    
    # Se não encontrou em nenhum lugar, retornar vazio (será tratado pelo offline agent)
    return api_key

def get_llm_config() -> Dict[str, Any]:
    """Retorna configuração do LLM com API key dos secrets."""
    api_key = get_api_key()
    
    if not api_key:
        # Retornar config vazia para trigger do modo offline
        raise ValueError("⚠️ API key não configurada. Configure OPENROUTER_API_KEY nos secrets.")
    
    return {
        "model_name": "deepseek/deepseek-chat-v3.1:free",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": api_key,
        "temperature": 0.1,
        "max_tokens": 2000
    }

class Settings:
    """Classe para gerenciar todas as configurações da aplicação."""
    
    # Configuração do LLM (lazy loading via property)
    @property
    def LLM_CONFIG(self) -> Dict[str, Any]:
        return get_llm_config()
    
    # Configurações de Memória
    MEMORY_CONFIG: Dict[str, Any] = {
        "window_size": 10,  # Número de interações para manter em memória
        "return_messages": True
    }
    
    # Configurações do Agente
    AGENT_CONFIG: Dict[str, Any] = {
        "verbose": True,
        "max_iterations": 10,  # Aumentado para permitir mais análises
        "handle_parsing_errors": True,
        "return_intermediate_steps": True,
        "max_execution_time": 120,  # Aumentado para permitir análises mais complexas
        "early_stopping_method": "generate"  # Força o agente a gerar uma resposta final
    }
    
    # Configurações da Interface
    UI_CONFIG: Dict[str, Any] = {
        "page_title": "🤖 I2A2 EDA Agent - Análise Exploratória Inteligente",
        "page_icon": "📊",
        "layout": "wide"
    }
    
    # Configurações de Logging
    LOGGING_CONFIG: Dict[str, Any] = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
    
    # Configurações de Visualização
    VISUALIZATION_CONFIG: Dict[str, Any] = {
        "max_columns_boxplot": 20,  # Máximo de colunas para boxplot múltiplo
        "subplot_max_cols": 3,  # Máximo de colunas em subplots
        "default_height": 500,
        "color_scheme": "#1f77b4"
    }

# Instância única de configurações
settings = Settings()
