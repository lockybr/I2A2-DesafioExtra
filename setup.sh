#!/bin/bash
# Script de setup para produção

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup completo! Execute: streamlit run app_refatorado.py"
