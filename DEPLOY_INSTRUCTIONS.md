# 🚀 Instruções de Deploy - I2A2 EDA Agent

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- 2GB de espaço em disco livre
- Conexão com internet (para instalação de dependências)

## 🔧 Instalação

### 1. Extrair os arquivos
Extraia todos os arquivos deste ZIP para um diretório de sua escolha.

### 2. Criar ambiente virtual (recomendado)
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

## 🚀 Executar a Aplicação

### Desenvolvimento/Teste local
```bash
streamlit run app_refatorado.py
```

A aplicação será aberta automaticamente em: http://localhost:8501

### Produção

#### Opção 1: Streamlit Community Cloud
1. Faça upload dos arquivos para um repositório GitHub
2. Acesse https://share.streamlit.io
3. Conecte seu repositório
4. Deploy automático!

#### Opção 2: Docker
```bash
# Criar Dockerfile (exemplo)
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app_refatorado.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build e executar
docker build -t i2a2-eda-agent .
docker run -p 8501:8501 i2a2-eda-agent
```

#### Opção 3: Servidor Linux com Nginx
```bash
# Instalar dependências do sistema
sudo apt-get update
sudo apt-get install python3-pip python3-venv nginx

# Configurar aplicação
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Executar com nohup
nohup streamlit run app_refatorado.py --server.port=8501 &

# Configurar Nginx como proxy reverso
# Editar /etc/nginx/sites-available/default
location /eda-agent {
    proxy_pass http://localhost:8501;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

## 🔐 Configuração de API Keys

O projeto usa modelos LLM gratuitos através do OpenRouter. 
As chaves já estão configuradas no código, mas você pode:

1. Criar sua própria conta em https://openrouter.ai
2. Obter uma API key gratuita
3. Atualizar em `config/settings.py` ou via variável de ambiente:

```bash
export OPENROUTER_API_KEY="sua-chave-aqui"
```

## 📊 Modelos LLM Disponíveis

- xAI Grok 4 Fast (gratuito, 100 req/dia)
- Meta Llama 3.2 3B (gratuito, 200 req/dia)
- DeepSeek Free (gratuito, 50 req/dia)

## 🐛 Troubleshooting

### Erro ao instalar dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Porta 8501 já em uso
```bash
streamlit run app_refatorado.py --server.port=8502
```

### Erro de memória com datasets grandes
- Reduza o tamanho do dataset
- Aumente a memória disponível
- Use amostragem dos dados

## 📈 Monitoramento

Para produção, considere adicionar:
- Logs estruturados (já implementados em utils/logger.py)
- Métricas de uso (Prometheus/Grafana)
- Health checks
- Rate limiting

## 🔒 Segurança

- ✅ Dados processados localmente
- ✅ Não compartilha dados com servidores externos
- ✅ Apenas perguntas são enviadas para LLMs
- ⚠️ Para produção, adicione autenticação (Streamlit Auth, OAuth, etc)

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique README.md para documentação completa
2. Consulte ARCHITECTURE.md para detalhes técnicos
3. Verifique os logs em caso de erros

## 📝 Checklist de Deploy

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas
- [ ] Aplicação rodando localmente
- [ ] Configuração de proxy/firewall (se necessário)
- [ ] Monitoramento configurado
- [ ] Backup dos dados configurado
- [ ] Documentação revisada

---
**Versão:** 2.0.3 | **Última atualização:** 2025
