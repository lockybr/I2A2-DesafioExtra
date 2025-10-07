"""
Sistema de fallback para LLMs com rate limiting.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import streamlit as st
from langchain_openai import ChatOpenAI
from config.settings_alternatives import alternative_settings

logger = logging.getLogger(__name__)

class LLMFallbackManager:
    """Gerenciador de fallback para LLMs com rate limiting."""
    
    def __init__(self):
        """Inicializa o gerenciador de fallback."""
        self.current_provider = 0
        self.rate_limit_tracker = {}
        self.last_error_time = {}
        self.current_provider_name = None
        self.current_provider_info = None
        
    def get_llm(self, force_provider: Optional[int] = None):
        """
        Obtém uma instância de LLM com fallback automático.
        
        Args:
            force_provider: Índice do provider para forçar uso
            
        Returns:
            ChatOpenAI: Instância configurada do LLM
        """
        print("🔄 Iniciando get_llm...")  # Print direto para debug
        providers = alternative_settings.get_fallback_configs()
        print(f"📚 Providers disponíveis: {[p['name'] for p in providers]}")  # Print direto para debug
        
        if force_provider is not None:
            provider = providers[force_provider]
            
            # Verificar API key
            if not provider['config'].get('api_key'):
                logger.error(f"API key não encontrada para {provider['name']}")
                if hasattr(st, 'error'):
                    st.error(f"❌ API key não encontrada para {provider['name']}")
                raise ValueError(f"API key não configurada para {provider['name']}")
            
            # Armazenar informações do provider forçado
            self.current_provider_name = provider['name']
            self.current_provider_info = provider
            
            logger.info(f"Forçando uso do provider: {provider['name']}")
            
            # Mostrar notificação no Streamlit
            if hasattr(st, 'info'):
                st.info(f"🎯 Usando modelo selecionado: {provider['name']}")
                
            # Log da configuração (sem a API key)
            safe_config = provider['config'].copy()
            if 'api_key' in safe_config:
                safe_config['api_key'] = f"length: {len(safe_config['api_key'])}"
            logger.info(f"Configuração do provider: {safe_config}")
            
            return self._create_llm(provider)
        
        # Tentar cada provider em ordem
        for i, provider in enumerate(providers):
            try:
                # Verificar se está em cooldown
                if self._is_in_cooldown(provider['name']):
                    logger.info(f"Provider {provider['name']} está em cooldown")
                    continue
                
                # Verificar se requer configuração especial
                if provider.get('requires_key') and not provider['config'].get('api_key'):
                    logger.info(f"Provider {provider['name']} requer API key")
                    continue
                    
                
                # Criar e testar LLM
                llm = self._create_llm(provider)
                
                # Armazenar informações do provider atual
                self.current_provider_name = provider['name']
                self.current_provider_info = provider
                
                logger.info(f"Usando provider: {provider['name']}")
                
                # Mostrar notificação no Streamlit
                if hasattr(st, 'info'):
                    st.info(f"🔄 Usando modelo: {provider['name']}")
                
                return llm
                
            except Exception as e:
                logger.error(f"Erro com provider {provider['name']}: {e}")
                self._mark_error(provider['name'])
                continue
        
        # Se todos falharam, retornar erro
        raise Exception("Todos os providers de LLM falharam. Verifique as configurações.")
    
    def _create_llm(self, provider: Dict[str, Any]):
        """Cria uma instância de LLM com a configuração do provider."""
        config = provider['config'].copy()
        
        # Remover campos vazios
        config = {k: v for k, v in config.items() if v}
        
        return ChatOpenAI(**config)
    
    def _is_in_cooldown(self, provider_name: str) -> bool:
        """Verifica se o provider está em período de cooldown."""
        if provider_name not in self.last_error_time:
            return False
        
        cooldown_until = self.last_error_time[provider_name] + timedelta(
            minutes=alternative_settings.RATE_LIMIT_CONFIG['cooldown_minutes']
        )
        
        return datetime.now() < cooldown_until
    
    def _mark_error(self, provider_name: str):
        """Marca um erro para o provider."""
        self.last_error_time[provider_name] = datetime.now()
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna o status dos providers."""
        status = {}
        for provider in alternative_settings.get_fallback_configs():
            name = provider['name']
            status[name] = {
                'available': not self._is_in_cooldown(name),
                'rate_limit': provider.get('rate_limit'),
                'is_free': provider.get('is_free', False),
                'last_error': self.last_error_time.get(name)
            }
        return status
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """Retorna informações do provider atualmente em uso."""
        if self.current_provider_info:
            return {
                'name': self.current_provider_name,
                'model': self.current_provider_info['config']['model_name'],
                'rate_limit': self.current_provider_info.get('rate_limit'),
                'is_free': self.current_provider_info.get('is_free', False),
                'context_length': self.current_provider_info.get('context_length', 'N/A')
            }
        return {'name': 'Nenhum', 'model': 'N/A'}

# Instância global
llm_fallback_manager = LLMFallbackManager()
