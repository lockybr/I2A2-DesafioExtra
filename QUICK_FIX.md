# 🔧 SOLUÇÃO RÁPIDA - Configure Agora!

## ⚠️ PROBLEMA
Sua aplicação no Streamlit Cloud está no modo offline porque falta configurar a API key.

## ✅ SOLUÇÃO (3 minutos)

### **1. Acesse o Streamlit Cloud**
- Vá em: https://share.streamlit.io/
- Entre na sua conta

### **2. Abra as Configurações**
- Encontre seu app: `i2a2desafioextra-saulobelchior`
- Clique em **⋮** (três pontos) > **Settings**

### **3. Configure a API Key**
1. Clique em **Secrets** no menu lateral
2. Cole isso na caixa de texto:

```toml
OPENROUTER_API_KEY = "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"
```

3. Clique em **Save**
4. Aguarde o app reiniciar (1-2 minutos)

### **4. Teste**
- Acesse: https://i2a2desafioextra-saulobelchior.streamlit.app/
- Faça upload de um CSV
- Faça uma pergunta
- **Deve funcionar agora!** ✨

---

## 📸 Visual do que fazer:

```
Streamlit Cloud > Seu App > ⋮ > Settings > Secrets

┌─────────────────────────────────────┐
│ Secrets                              │
├─────────────────────────────────────┤
│                                      │
│ OPENROUTER_API_KEY = "sk-or-v1-..." │
│                                      │
│                                      │
│                    [Save]   [Cancel] │
└─────────────────────────────────────┘
```

---

## 🎯 Resultado Esperado

**ANTES:**
```
❌ LLM indisponível. Usando modo offline...
```

**DEPOIS:**
```
🔄 Usando modelo: xAI Grok 4 Fast
✅ Análise completa!
```

---

## 🆘 Ainda não funcionou?

1. Verifique se salvou os secrets corretamente
2. Force o restart: Settings > Advanced > Reboot app
3. Veja o guia completo: `STREAMLIT_CLOUD_SETUP.md`

---

**É isso! Simples assim.** 🚀
