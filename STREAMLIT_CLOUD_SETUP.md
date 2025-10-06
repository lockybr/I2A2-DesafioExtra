# 🚀 Guia Completo: Como Configurar a Aplicação no Streamlit Cloud

## ❌ Problema
A aplicação está caindo no modo offline com a mensagem:
```
❌ LLM indisponível. Usando modo offline...
```

## ✅ Solução: Configurar API Key no Streamlit Cloud

### **Passo 1: Acesse as Configurações do Streamlit Cloud**

1. Acesse: https://share.streamlit.io/
2. Faça login na sua conta
3. Encontre seu app: `i2a2desafioextra-saulobelchior`
4. Clique nos três pontos (**⋮**) ao lado do app
5. Selecione **Settings** (Configurações)

### **Passo 2: Configure os Secrets**

1. No menu lateral, clique em **Secrets**
2. Cole o seguinte conteúdo na caixa de texto:

```toml
OPENROUTER_API_KEY = "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"
```

3. Clique em **Save** (Salvar)
4. O app vai reiniciar automaticamente

### **Passo 3: Verifique se Funcionou**

1. Aguarde o app reiniciar (geralmente 1-2 minutos)
2. Acesse novamente: https://i2a2desafioextra-saulobelchior.streamlit.app/
3. Faça upload de um arquivo CSV
4. Faça uma pergunta
5. Você deve ver a mensagem: `🔄 Usando modelo: xAI Grok 4 Fast` (ou outro modelo)
6. **NÃO DEVE** aparecer a mensagem de "LLM indisponível"

---

## 🔐 Obtendo sua Própria API Key (Opcional)

Se quiser usar sua própria API key do OpenRouter:

1. Acesse: https://openrouter.ai/
2. Crie uma conta (gratuita)
3. Vá em **Keys** no menu
4. Clique em **Create Key**
5. Copie a chave que começa com `sk-or-v1-...`
6. Substitua no secrets do Streamlit Cloud

**Modelos Gratuitos Disponíveis:**
- xAI Grok 4 Fast (2M tokens de contexto)
- Meta Llama 3.2 3B (128k tokens)
- DeepSeek Chat v3.1 (256k tokens)

---

## 💻 Desenvolvimento Local

Para rodar localmente:

1. Crie o arquivo `.streamlit/secrets.toml` (use o exemplo fornecido)
2. Adicione sua API key:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-sua-chave-aqui"
   ```
3. Execute: `streamlit run app_refatorado.py`

---

## 📁 Arquivos Modificados

Os seguintes arquivos foram atualizados para usar secrets:

- ✅ `config/settings.py` - Agora lê dos secrets do Streamlit
- ✅ `config/settings_alternatives.py` - Configurações de fallback atualizadas
- ✅ `utils/llm_fallback.py` - Sistema de fallback compatível
- ✅ `.streamlit/secrets.toml.example` - Template de configuração

---

## 🆘 Solução de Problemas

### Ainda aparece "LLM indisponível"?

1. **Verifique os secrets:**
   - Acesse Settings > Secrets no Streamlit Cloud
   - Confirme que `OPENROUTER_API_KEY` está configurada
   - Verifique se não há espaços extras antes/depois da chave

2. **Force o restart:**
   - Vá em Settings > Advanced
   - Clique em **Reboot app**

3. **Verifique os logs:**
   - Na página do app, clique em **Manage app**
   - Veja os logs para identificar erros específicos

4. **Teste a API key:**
   ```bash
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer sk-or-v1-sua-chave-aqui"
   ```

### API Key inválida ou expirada?

- Obtenha uma nova em: https://openrouter.ai/keys
- Atualize nos secrets do Streamlit Cloud
- Reinicie o app

---

## 🎯 Resultado Esperado

Após a configuração correta, você verá:

✅ **Antes (com erro):**
```
❌ LLM indisponível. Usando modo offline...
🤖 Modo Offline: Usando análise baseada em regras (LLM indisponível)
```

✅ **Depois (funcionando):**
```
🔄 Usando modelo: xAI Grok 4 Fast
🤖 Analisando seus dados com IA...
```

---

## 📚 Recursos Adicionais

- **Documentação do Streamlit Secrets:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- **OpenRouter Docs:** https://openrouter.ai/docs
- **Modelos Gratuitos:** https://openrouter.ai/models?pricing=free

---

**✨ Pronto! Sua aplicação agora deve funcionar corretamente no Streamlit Cloud.**
