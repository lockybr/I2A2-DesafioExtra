"""
Script de teste para verificar se os secrets estão configurados corretamente.
Execute com: streamlit run test_secrets.py
"""

import streamlit as st
import os

st.title("🔍 Teste de Secrets - Diagnóstico")

st.markdown("---")

# Teste 1: Verificar se st.secrets existe
st.subheader("1️⃣ st.secrets está disponível?")
if hasattr(st, 'secrets'):
    st.success("✅ SIM - st.secrets está disponível")
    
    # Listar todas as chaves
    try:
        keys = list(st.secrets.keys())
        st.info(f"📋 Chaves encontradas nos secrets: {keys}")
    except Exception as e:
        st.error(f"❌ Erro ao listar chaves: {e}")
else:
    st.error("❌ NÃO - st.secrets não está disponível")

st.markdown("---")

# Teste 2: Verificar OPENROUTER_API_KEY
st.subheader("2️⃣ OPENROUTER_API_KEY está configurada?")
try:
    if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
        api_key = st.secrets['OPENROUTER_API_KEY']
        st.success(f"✅ SIM - API key encontrada!")
        st.info(f"📏 Tamanho da chave: {len(api_key)} caracteres")
        st.info(f"🔒 Primeiros 10 caracteres: {api_key[:10]}...")
        st.info(f"🔒 Últimos 10 caracteres: ...{api_key[-10:]}")
    else:
        st.error("❌ NÃO - OPENROUTER_API_KEY não encontrada nos secrets")
except Exception as e:
    st.error(f"❌ Erro ao acessar OPENROUTER_API_KEY: {e}")

st.markdown("---")

# Teste 3: Verificar variável de ambiente
st.subheader("3️⃣ Variável de ambiente OPENROUTER_API_KEY?")
env_key = os.getenv('OPENROUTER_API_KEY')
if env_key:
    st.info(f"✅ Encontrada na variável de ambiente (length: {len(env_key)})")
else:
    st.warning("❌ Não encontrada em variável de ambiente (normal em produção)")

st.markdown("---")

# Teste 4: Testar conexão com OpenRouter
st.subheader("4️⃣ Testar conexão com OpenRouter")

if st.button("🧪 Testar API Key"):
    try:
        if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
            api_key = st.secrets['OPENROUTER_API_KEY']
            
            # Tentar criar uma LLM
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                model_name="deepseek/deepseek-chat-v3.1:free",
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                temperature=0.1,
                max_tokens=100
            )
            
            st.info("🔄 Testando conexão...")
            
            # Fazer uma chamada simples
            response = llm.invoke("Responda apenas: OK")
            
            st.success("✅ API KEY FUNCIONA!")
            st.success(f"Resposta da LLM: {response.content}")
        else:
            st.error("❌ Não foi possível testar - API key não encontrada")
    except Exception as e:
        st.error(f"❌ Erro ao testar API: {e}")
        import traceback
        with st.expander("🔍 Detalhes do erro"):
            st.code(traceback.format_exc())

st.markdown("---")

# Instruções
st.subheader("📝 Como Configurar os Secrets")
st.markdown("""
### No Streamlit Cloud:

1. Vá em **Settings** > **Secrets**
2. Cole isto na caixa de texto:

```toml
OPENROUTER_API_KEY = "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"
```

3. Clique em **Save**
4. Aguarde 1-2 minutos para o app reiniciar

### Localmente:

Crie o arquivo `.streamlit/secrets.toml` com:

```toml
OPENROUTER_API_KEY = "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"
```
""")
