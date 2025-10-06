"""
Ferramentas de análise de dados para o EDA Agent.
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import logging
from typing import Optional
from langchain.tools import tool

logger = logging.getLogger(__name__)

@tool
def get_data_description() -> str:
    """
    Útil para obter uma visão geral do DataFrame, incluindo tipos de dados, 
    contagens de valores nulos e valores únicos por coluna.
    """
    logger.info("Executing get_data_description")
    logger.info(f"Session state keys: {list(st.session_state.keys())}")
    
    # Acessar o DataFrame do session_state
    if 'df' not in st.session_state:
        logger.error("'df' key not found in session_state")
        logger.error(f"Available keys: {list(st.session_state.keys())}")
        return "❌ Erro: Nenhum dado foi carregado ainda. Por favor, faça upload de um arquivo CSV."
    
    if st.session_state.df is None:
        logger.error("DataFrame is None in session_state")
        return "❌ Erro: O DataFrame está vazio. Por favor, faça upload de um arquivo CSV."
    
    df = st.session_state.df
    logger.info(f"✅ Successfully accessed DataFrame with shape: {df.shape}")
    logger.info(f"DataFrame columns: {list(df.columns)[:5]}..." if len(df.columns) > 5 else f"DataFrame columns: {list(df.columns)}")
    
    buffer = io.StringIO()
    
    # Informações gerais
    buffer.write("📊 **Informações Gerais do Dataset:**\n\n")
    buffer.write(f"- Dimensões: {df.shape[0]:,} linhas × {df.shape[1]} colunas\n")
    buffer.write(f"- Tamanho em memória: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n\n")
    
    # Informações por coluna
    buffer.write("**Detalhes das Colunas:**\n\n")
    
    info_df = pd.DataFrame({
        'Tipo': df.dtypes.astype(str),
        'Valores Nulos': df.isnull().sum(),
        '% Nulos': (df.isnull().sum() / len(df) * 100).round(2),
        'Valores Únicos': df.nunique(),
        '% Únicos': (df.nunique() / len(df) * 100).round(2)
    })
    
    buffer.write(info_df.to_string())
    
    # Resumo dos tipos de dados
    buffer.write("\n\n**Resumo dos Tipos de Dados:**\n")
    type_counts = df.dtypes.value_counts()
    for dtype, count in type_counts.items():
        buffer.write(f"- {dtype}: {count} coluna(s)\n")
    
    return buffer.getvalue()


@tool
def get_descriptive_statistics(column: Optional[str] = None) -> str:
    """
    Calcula estatísticas descritivas como média, mediana, desvio padrão, 
    mínimo e máximo para colunas numéricas. Se nenhuma coluna for especificada, 
    calcula para todo o DataFrame.
    """
    logger.info(f"Executing get_descriptive_statistics for column: {column}")
    logger.info(f"Session state has 'df': {'df' in st.session_state}")
    
    # Acessar o DataFrame do session_state
    if 'df' not in st.session_state:
        logger.error("'df' key not found in session_state")
        return "❌ Erro: Nenhum dado foi carregado ainda. Por favor, faça upload de um arquivo CSV."
    
    if st.session_state.df is None:
        logger.error("DataFrame is None in session_state")
        return "❌ Erro: O DataFrame está vazio. Por favor, faça upload de um arquivo CSV."
    
    df = st.session_state.df
    logger.info(f"✅ Successfully accessed DataFrame with shape: {df.shape}")
    
    if column:
        logger.info(f"Calculating statistics for column: {column}")
        if column not in df.columns:
            return f"❌ Erro: A coluna '{column}' não existe no DataFrame."
        
        if not pd.api.types.is_numeric_dtype(df[column]):
            return f"⚠️ A coluna '{column}' não é numérica. Estatísticas não podem ser calculadas."
        
        stats = df[column].describe()
        result = f"📈 **Estatísticas Descritivas para '{column}':**\n\n"
        result += stats.to_string()
        
        # Adicionar informações extras
        result += f"\n\n**Informações Adicionais:**\n"
        result += f"- Variância: {df[column].var():.4f}\n"
        result += f"- Assimetria (Skewness): {df[column].skew():.4f}\n"
        result += f"- Curtose: {df[column].kurtosis():.4f}\n"
        result += f"- Coeficiente de Variação: {(df[column].std() / df[column].mean() * 100):.2f}%"
        
    else:
        # Estatísticas para todas as colunas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return "⚠️ Não há colunas numéricas no DataFrame."
        
        stats = df[numeric_cols].describe()
        result = "📈 **Estatísticas Descritivas para Todas as Colunas Numéricas:**\n\n"
        result += stats.to_string()
        
    return result
