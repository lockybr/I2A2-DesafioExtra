# 🔗 Guia Completo: Conectar Projeto ao GitHub

## 📋 Pré-requisitos

### 1. Instalar Git
Se você ainda não tem Git instalado:

1. **Baixe o Git:**
   - Acesse: https://git-scm.com/download/win
   - Baixe a versão para Windows
   - Execute o instalador
   - **IMPORTANTE:** Durante a instalação, marque "Git from the command line and also from 3rd-party software"

2. **Verifique a instalação:**
   - Abra um NOVO PowerShell (feche e abra novamente)
   - Digite: `git --version`
   - Deve mostrar algo como: `git version 2.x.x`

### 2. Configurar Git (Primeira vez)
```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

---

## 🚀 Método 1: Usar GitHub Desktop (MAIS FÁCIL)

### Passo 1: Instalar GitHub Desktop
1. Acesse: https://desktop.github.com/
2. Baixe e instale
3. Faça login com sua conta GitHub

### Passo 2: Adicionar Repositório Local
1. Abra GitHub Desktop
2. File > Add Local Repository
3. Navegue até: `c:\labz\versão-final\sssAgentes Autônomos – Atividade Extra`
4. Se pedir para inicializar, clique em "create a repository"

### Passo 3: Fazer Commit
1. Na aba "Changes", você verá todos os arquivos modificados
2. **IMPORTANTE:** Desmarque o arquivo `fix_settings.py` (não queremos commitar ele)
3. Escreva a mensagem de commit:
   ```
   fix: Configurar API keys via Streamlit Secrets
   
   - Atualizado settings.py para ler OPENROUTER_API_KEY dos secrets
   - Corrigido settings_alternatives.py com lazy loading
   - Melhorado tratamento de erros em eda_agent.py
   - Removido hardcoded API keys do código
   ```
4. Clique em "Commit to main"

### Passo 4: Publicar no GitHub
1. Clique em "Publish repository"
2. Escolha:
   - Name: `i2a2-eda-agent` (ou o nome que preferir)
   - Description: "Sistema de Análise Exploratória de Dados com IA"
   - ☑️ Keep this code private (se quiser privado)
3. Clique em "Publish Repository"

**PRONTO!** Seu código está no GitHub! 🎉

---

## 🚀 Método 2: Via Linha de Comando (Avançado)

### Opção A: Projeto Já Tem Git

Se o projeto já está conectado ao GitHub:

```powershell
# 1. Navegar até o projeto
cd "c:\labz\versão-final\sssAgentes Autônomos – Atividade Extra"

# 2. Deletar arquivo temporário
Remove-Item "fix_settings.py" -Force

# 3. Ver o que mudou
git status

# 4. Adicionar todas as mudanças
git add .

# 5. Fazer commit
git commit -m "fix: Configurar API keys via Streamlit Secrets"

# 6. Enviar para GitHub
git push origin main
```

### Opção B: Projeto Novo (Criar do Zero)

```powershell
# 1. Navegar até o projeto
cd "c:\labz\versão-final\sssAgentes Autônomos – Atividade Extra"

# 2. Inicializar Git
git init

# 3. Deletar arquivo temporário
Remove-Item "fix_settings.py" -Force

# 4. Adicionar todos os arquivos
git add .

# 5. Primeiro commit
git commit -m "feat: Aplicação EDA Agent com multi-LLM e Streamlit"

# 6. Criar repositório no GitHub (via navegador)
# - Acesse: https://github.com/new
# - Nome: i2a2-eda-agent
# - Descrição: Sistema de Análise Exploratória de Dados com IA
# - Privado ou Público
# - NÃO marque "Add README" (já temos)
# - Clique em "Create repository"

# 7. Conectar ao repositório remoto (substitua SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/i2a2-eda-agent.git

# 8. Enviar código
git branch -M main
git push -u origin main
```

---

## 🔄 Conectar ao Streamlit Cloud

Depois de ter o código no GitHub:

### 1. Acesse Streamlit Cloud
- Vá em: https://share.streamlit.io/

### 2. Deploy New App
1. Clique em "New app"
2. Escolha:
   - **Repository:** SEU_USUARIO/i2a2-eda-agent
   - **Branch:** main
   - **Main file path:** app_refatorado.py
3. **Advanced settings** > **Secrets:**
   ```toml
   OPENROUTER_API_KEY = "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"
   ```
4. Clique em "Deploy!"

### 3. Aguardar
- Deploy leva 2-5 minutos
- Você receberá uma URL tipo: https://seu-app.streamlit.app/

---

## 📝 Checklist de Verificação

Antes de fazer commit/push:

- [ ] Git instalado e configurado
- [ ] `fix_settings.py` deletado ou não incluído no commit
- [ ] `.gitignore` está protegendo `.streamlit/secrets.toml`
- [ ] Testou localmente (opcional)
- [ ] Secrets configurados no Streamlit Cloud

---

## 🆘 Problemas Comuns

### "git: command not found"
**Solução:** Instale o Git ou use GitHub Desktop

### "Permission denied (publickey)"
**Solução:** Configure SSH ou use HTTPS:
```powershell
git remote set-url origin https://github.com/SEU_USUARIO/i2a2-eda-agent.git
```

### "refusing to merge unrelated histories"
**Solução:**
```powershell
git pull origin main --allow-unrelated-histories
git push origin main
```

### Arquivo muito grande
**Solução:** Adicione ao `.gitignore`:
```
*.csv
*.xlsx
*.parquet
venv/
__pycache__/
```

---

## 🎯 Próximos Passos Após Deploy

1. **Teste a aplicação:**
   - Acesse a URL do Streamlit Cloud
   - Faça upload de um CSV
   - Verifique se mostra: `🔄 Usando modelo: xAI Grok 4 Fast`

2. **Configure CI/CD automático:**
   - Cada push no GitHub = redeploy automático no Streamlit

3. **Compartilhe:**
   - Sua URL ficará pública (se escolheu público)
   - Exemplo: https://i2a2desafioextra-saulobelchior.streamlit.app/

---

## 📞 Precisa de Ajuda?

**GitHub Desktop (Recomendado para iniciantes):**
- Tutorial: https://docs.github.com/en/desktop

**Git Command Line:**
- Guia: https://git-scm.com/book/pt-br/v2

**Streamlit Cloud:**
- Docs: https://docs.streamlit.io/streamlit-community-cloud

---

**🚀 Escolha um método acima e siga os passos!**
