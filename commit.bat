@echo off
echo ========================================
echo   SCRIPT DE COMMIT PARA GITHUB
echo ========================================
echo.

REM Configurar usuario do Git
git config --global user.name "lockybr"
git config --global user.email "saulo.belchior@gmail.com"
echo [OK] Usuario configurado

REM Inicializar repositorio (se necessario)
git init
echo [OK] Repositorio inicializado

REM Adicionar todos os arquivos
git add .
echo [OK] Arquivos adicionados

REM Fazer commit
git commit -m "fix: Configurar API keys via Streamlit Secrets - Resolve modo offline"
echo [OK] Commit realizado

echo.
echo ========================================
echo   COMMIT CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Proximos passos:
echo 1. No VS Code, va em Source Control
echo 2. Clique em "Publish Branch"
echo 3. Escolha o nome: i2a2-eda-agent
echo 4. Aguarde o Streamlit Cloud fazer redeploy
echo.
pause
