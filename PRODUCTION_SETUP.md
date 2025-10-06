# 🚀 Guia de Setup em Produção - EDA Agent

## 📋 Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API do OpenRouter (gratuita)

## 🔧 Instalação Rápida

### Windows (PowerShell)

```powershell
# 1. Extrair o ZIP
Expand-Archive eda_agent_production.zip -DestinationPath eda_agent

# 2. Entrar na pasta
cd eda_agent

# 3. Executar setup
.\setup.ps1

# 4. Configurar API Key
# Edite o arquivo .env e adicione sua chave do OpenRouter
notepad .env

# 5. Executar aplicação
streamlit run app_refatorado.py
```

### Linux/Mac (Bash)

```bash
# 1. Extrair o ZIP
unzip eda_agent_production.zip -d eda_agent

# 2. Entrar na pasta
cd eda_agent

# 3. Executar setup
chmod +x setup.sh
./setup.sh

# 4. Configurar API Key
# Edite o arquivo .env e adicione sua chave do OpenRouter
nano .env

# 5. Executar aplicação
streamlit run app_refatorado.py
```

## 🐳 Deploy com Docker

```bash
# 1. Configurar variável de ambiente
export OPENROUTER_API_KEY=sua_chave_aqui

# 2. Build e execução
docker-compose up -d

# 3. Acessar
# http://localhost:8501
```

## ☁️ Deploy em Cloud

### Streamlit Cloud (Recomendado - Gratuito)

1. Fazer fork do projeto no GitHub
2. Acessar [share.streamlit.io](https://share.streamlit.io)
3. Conectar repositório
4. Adicionar secrets:
   - `OPENROUTER_API_KEY = "sua_chave"`
5. Deploy automático!

### Heroku

```bash
# 1. Login
heroku login

# 2. Criar app
heroku create eda-agent-app

# 3. Configurar API Key
heroku config:set OPENROUTER_API_KEY=sua_chave

# 4. Deploy
git push heroku main
```

### AWS EC2 / DigitalOcean / Outros

```bash
# 1. SSH no servidor
ssh usuario@servidor

# 2. Clonar/copiar código
git clone seu_repositorio
# ou scp os arquivos

# 3. Executar setup
./setup.sh

# 4. Executar com nohup ou systemd
nohup streamlit run app_refatorado.py --server.port=8501 &
```

## 🔑 Obtendo API Key do OpenRouter

1. Acesse: https://openrouter.ai
2. Faça login/cadastro (gratuito)
3. Vá em "Keys" no menu
4. Crie uma nova chave
5. Copie e cole no arquivo `.env`

**Modelos Gratuitos Disponíveis:**
- DeepSeek Chat (Recomendado)
- Google Gemini Flash
- Meta Llama 3.1
- Mistral 7B

## 📊 Configuração de Produção

### Arquivo `.env`

```env
# API Keys
OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui

# Configurações do Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Limites
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
```

### Configurações de Performance

No arquivo `config/settings.py`, ajuste:

```python
AGENT_CONFIG = {
    "max_iterations": 10,
    "max_execution_time": 120,
}
```

## 🔒 Segurança

**IMPORTANTE:**
- ✅ NUNCA commite o arquivo `.env` com suas chaves
- ✅ Use `.env.example` como template
- ✅ Mantenha `requirements.txt` atualizado
- ✅ Use HTTPS em produção
- ✅ Configure rate limiting se expor publicamente

## 📈 Monitoramento

### Logs

```bash
# Ver logs em tempo real
tail -f logs/eda_agent.log

# Docker logs
docker-compose logs -f
```

### Health Check

Acesse: `http://seu-servidor:8501/_stcore/health`

## 🆘 Troubleshooting

### Erro: "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### Erro: "API Key invalid"
- Verifique se a chave está correta no `.env`
- Teste em: https://openrouter.ai/playground

### Erro: "Port already in use"
```bash
# Mudar porta
streamlit run app_refatorado.py --server.port=8502
```

### Performance lenta
- Reduza `max_iterations` em `config/settings.py`
- Use modelo mais rápido (Gemini Flash)
- Aumente recursos do servidor

## 📞 Suporte

- 📧 Email: suporte@exemplo.com
- 📚 Documentação: Ver DOCUMENTATION.md
- 🐛 Issues: GitHub Issues

## 📝 Checklist de Deploy

- [ ] Python 3.10+ instalado
- [ ] Dependências instaladas (`requirements.txt`)
- [ ] API Key configurada (`.env`)
- [ ] Porta 8501 liberada no firewall
- [ ] Testado localmente
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Documentação revisada

**Pronto! Sua aplicação está rodando em produção! 🎉**
