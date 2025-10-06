#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDA Agent - Aplicação de Análise Exploratória de Dados com IA
Arquitetura modular com Streamlit, LangChain e DeepSeek

Autor: EDA Agent Team
Versão: 2.0.0
"""

import streamlit as st
from config.settings import settings
from utils.logger import setup_logging
from ui import (
    initialize_session_state,
    render_sidebar,
    render_chat_interface,
    render_suggestions,
    render_history
)

# Configurar logging
logger = setup_logging()

def main():
    """
    Função principal da aplicação EDA Agent.
    """
    # Configurar página
    st.set_page_config(
        page_title=settings.UI_CONFIG["page_title"],
        page_icon=settings.UI_CONFIG["page_icon"],
        layout=settings.UI_CONFIG["layout"]
    )
    
    # DEBUG: Verificar secrets (remover em produção)
    if hasattr(st, 'secrets'):
        logger.info("✅ Secrets disponível no Streamlit")
        available_keys = list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else []
        logger.info(f"Chaves nos secrets: {available_keys}")
        if 'OPENROUTER_API_KEY' in st.secrets:
            api_key_length = len(st.secrets['OPENROUTER_API_KEY'])
            logger.info(f"✅ OPENROUTER_API_KEY encontrada (length: {api_key_length})")
        else:
            logger.error("❌ OPENROUTER_API_KEY NÃO encontrada nos secrets!")
            logger.error(f"Secrets disponíveis: {available_keys}")
    else:
        logger.error("❌ st.secrets NÃO está disponível!")
    
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Título e descrição
    st.title("🤖 I2A2 EDA Agent")
    st.markdown("""
    **Bem-vindo ao I2A2 EDA Agent!** 
    
    Esta aplicação combina o poder do Streamlit com a inteligência do LangChain e múltiplas LLMs 
    para fornecer análises exploratórias de dados de forma interativa e inteligente.
    
    ### ✨ Funcionalidades:
    - 🔍 Análise automática de dados com IA
    - 📊 Visualizações interativas e dinâmicas
    - 🧠 Memória de contexto para análises cumulativas
    - 🎯 Geração automática de insights e conclusões
    """)
    
    # Renderizar sidebar com upload e configurações
    render_sidebar()
    
    # Renderizar interface de chat principal
    render_chat_interface()
    
    # Renderizar sugestões de perguntas
    if st.session_state.df is not None:
        render_suggestions()
        render_history()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>I2A2 - EDA Agents & Multi-LLM & LangChain & Modular Architecture | Powered by Saulo Belchior</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except KeyError as ke:
        logger.error(f"KeyError in main: {ke}")
        import traceback
        logger.error(traceback.format_exc())
        
        st.error(f"❌ Erro de chave não encontrada: {str(ke)}")
        st.info("💡 Isso geralmente ocorre quando há dados inconsistentes no histórico.")
        
        if st.button("🔄 Limpar Sessão e Recarregar"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        st.error(f"❌ Erro crítico na aplicação: {str(e)}")
        st.error("Por favor, recarregue a página ou contate o suporte.")
        
        with st.expander("🔍 Detalhes do erro"):
            st.code(traceback.format_exc())
