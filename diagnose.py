"""
Script de diagnóstico para testar a configuração do LLM
"""

import streamlit as st
from config.settings import get_api_key
from utils.llm_fallback import llm_fallback_manager
from config.settings_alternatives import alternative_settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("\n=== Iniciando Diagnóstico ===\n")
    
    # 1. Verificar secrets do Streamlit
    print("\n1. Verificando Streamlit secrets...")
    if hasattr(st, 'secrets'):
        print("✅ st.secrets está disponível")
        if hasattr(st.secrets, 'keys'):
            keys = list(st.secrets.keys())
            print(f"📝 Chaves disponíveis: {keys}")
        else:
            print("⚠️ st.secrets não tem método keys()")
    else:
        print("❌ st.secrets NÃO está disponível")
    
    # 2. Verificar API Key
    print("\n2. Verificando API Key...")
    api_key = get_api_key()
    if api_key:
        print(f"✅ API Key encontrada (length: {len(api_key)})")
        print(f"Primeiros 10 caracteres: {api_key[:10]}...")
    else:
        print("❌ API Key não encontrada!")
    
    # 3. Verificar configurações de fallback
    print("\n3. Verificando configurações de fallback...")
    configs = alternative_settings.get_fallback_configs()
    print(f"📚 {len(configs)} providers configurados:")
    for i, config in enumerate(configs):
        name = config['name']
        has_key = bool(config['config'].get('api_key'))
        print(f"{i+1}. {name}: {'✅ tem key' if has_key else '❌ sem key'}")
    
    # 4. Tentar criar LLM
    print("\n4. Tentando criar LLM...")
    try:
        llm = llm_fallback_manager.get_llm()
        print("✅ LLM criado com sucesso!")
        
        print("\n5. Testando LLM...")
        try:
            response = llm.invoke("Responda apenas com OK se estiver funcionando.")
            print(f"✅ Resposta do LLM: {response}")
        except Exception as e:
            print(f"❌ Erro ao testar LLM: {str(e)}")
            
    except Exception as e:
        print(f"❌ Erro ao criar LLM: {str(e)}")
    
    print("\n=== Diagnóstico Concluído ===\n")

if __name__ == "__main__":
    main()