"""
Configuração de memória para o EDA Agent.
"""

import streamlit as st
import logging
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage
from config.settings import settings

logger = logging.getLogger(__name__)

def create_memory(llm):
    """
    Cria e configura a memória para o agente.
    
    Args:
        llm: Instância do modelo de linguagem
        
    Returns:
        ConversationBufferWindowMemory: Memória configurada
    """
    try:
        # Usar ConversationBufferWindowMemory que mantém as últimas K mensagens
        memory = ConversationBufferWindowMemory(
            k=settings.MEMORY_CONFIG["window_size"],
            return_messages=settings.MEMORY_CONFIG["return_messages"],
            memory_key="chat_history",
            output_key="output"  # Especificar a chave de saída para evitar warning
        )
        logger.info(f"Memory configured successfully with window size of {settings.MEMORY_CONFIG['window_size']}")
        
        # Carregar histórico existente se houver
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            # Carregar apenas as últimas mensagens para não sobrecarregar
            messages_to_load = st.session_state.chat_history[-(settings.MEMORY_CONFIG["window_size"] * 2):]
            
            for msg in messages_to_load:
                if isinstance(msg, HumanMessage):
                    memory.chat_memory.add_user_message(msg.content)
                elif isinstance(msg, AIMessage):
                    memory.chat_memory.add_ai_message(msg.content)
            
            logger.info(f"Loaded {len(messages_to_load)} messages into memory")
        
        return memory
        
    except Exception as e:
        logger.error(f"Error configuring memory: {e}")
        return None


def save_to_history(prompt: str, response: str, tools_used: list = None):
    """
    Salva uma interação no histórico de análises.
    
    Args:
        prompt: Pergunta do usuário
        response: Resposta do agente
        tools_used: Lista de ferramentas utilizadas
    """
    from datetime import datetime
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    st.session_state.analysis_history.append({
        'timestamp': datetime.now().isoformat(),
        'query': prompt,
        'response': response,
        'tools_used': tools_used or []
    })
    
    logger.info(f"Saved interaction to history. Total interactions: {len(st.session_state.analysis_history)}")
