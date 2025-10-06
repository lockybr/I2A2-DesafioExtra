"""
Callbacks personalizados para o EDA Agent.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
import logging
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger(__name__)

class StreamlitCallbackHandler(BaseCallbackHandler):
    """Callback handler para exibir progresso no Streamlit."""
    
    def __init__(self, container):
        """
        Inicializa o callback handler.
        
        Args:
            container: Container do Streamlit para exibir mensagens
        """
        self.container = container
        self.steps = []
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Quando uma ferramenta começa a executar."""
        if serialized is None:
            return
        tool_name = serialized.get("name", "Ferramenta")
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🔧 [{timestamp}] Executando: **{tool_name}**"
        logger.info(f"Tool started: {tool_name}")
        self.steps.append(message)
        self.update_display()
        
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Quando uma ferramenta termina."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"✅ [{timestamp}] Ferramenta concluída"
        logger.info(f"Tool completed")
        self.steps.append(message)
        self.update_display()
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Quando o LLM começa a processar."""
        if serialized is None:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Obter o nome do modelo atual
        model_name = "LLM"
        try:
            from utils.llm_fallback import llm_fallback_manager
            provider_info = llm_fallback_manager.get_current_provider_info()
            if provider_info['name'] != 'Nenhum':
                model_name = provider_info['name']
        except:
            pass
        
        message = f"🤖 [{timestamp}] {model_name} analisando pergunta..."
        logger.info(f"LLM processing started with {model_name}")
        self.steps.append(message)
        self.update_display()
        
    def on_llm_end(self, response, **kwargs) -> None:
        """Quando o LLM termina."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Obter o nome do modelo atual
        model_name = "LLM"
        try:
            from utils.llm_fallback import llm_fallback_manager
            provider_info = llm_fallback_manager.get_current_provider_info()
            if provider_info['name'] != 'Nenhum':
                model_name = provider_info['name']
        except:
            pass
        
        message = f"💡 [{timestamp}] {model_name} decidiu a melhor abordagem"
        logger.info(f"LLM processing completed with {model_name}")
        self.steps.append(message)
        self.update_display()
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Quando uma cadeia começa a executar."""
        if serialized is None:
            return
        chain_name = serialized.get("name", "Chain")
        if chain_name != "AgentExecutor":  # Evitar logs redundantes
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"🔄 [{timestamp}] Iniciando: {chain_name}"
            logger.info(f"Chain started: {chain_name}")
            self.steps.append(message)
            self.update_display()
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Quando uma cadeia termina."""
        pass  # Evitar muitos logs
        
    def on_agent_action(self, action, **kwargs) -> None:
        """Quando o agente executa uma ação."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        tool = action.tool if hasattr(action, 'tool') else 'Ação'
        message = f"🎯 [{timestamp}] Agente executando: {tool}"
        logger.info(f"Agent action: {tool}")
        self.steps.append(message)
        self.update_display()
    
    def on_agent_finish(self, finish, **kwargs) -> None:
        """Quando o agente termina."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🏁 [{timestamp}] Agente concluiu análise"
        logger.info("Agent finished")
        self.steps.append(message)
        self.update_display()
    
    def update_display(self):
        """Atualiza a exibição no Streamlit."""
        with self.container:
            # Limpar container antes de atualizar
            self.container.empty()
            
            # Mostrar últimos 5 passos
            with self.container.container():
                for step in self.steps[-5:]:
                    st.markdown(step)
    
    def clear(self):
        """Limpa os passos armazenados."""
        self.steps = []
        self.container.empty()
