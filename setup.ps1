# Script de setup para Windows PowerShell

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Setup completo! Execute: streamlit run app_refatorado.py"
