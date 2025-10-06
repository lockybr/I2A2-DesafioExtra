"""
Ferramenta de geração de insights e conclusões para o EDA Agent.
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from langchain.tools import tool

logger = logging.getLogger(__name__)

@tool
def generate_insights_and_conclusions() -> str:
    """
    Analisa todos os resultados anteriores e gera insights e conclusões 
    baseados nas análises já realizadas durante a sessão.
    """
    logger.info("Generating insights and conclusions")
    logger.info(f"Session state has 'df': {'df' in st.session_state}")
    logger.info(f"Session state has 'analysis_history': {'analysis_history' in st.session_state}")
    
    if 'analysis_history' not in st.session_state:
        return "⚠️ Ainda não foram realizadas análises suficientes para gerar conclusões."
    
    if 'df' not in st.session_state:
        logger.error("'df' key not found in session_state")
        return "❌ Erro: Nenhum dado foi carregado ainda. Por favor, faça upload de um arquivo CSV."
    
    if st.session_state.df is None:
        logger.error("DataFrame is None in session_state")
        return "❌ Erro: O DataFrame está vazio. Por favor, faça upload de um arquivo CSV."
    
    df = st.session_state.df
    logger.info(f"✅ Successfully accessed DataFrame with shape: {df.shape}")
    history = st.session_state.analysis_history
    
    insights = []
    insights.append("## 🎯 Insights e Conclusões Baseados nas Análises\n")
    
    # Análise do dataset
    insights.append(f"### 📊 Características do Dataset:")
    insights.append(f"- **Volume de dados**: {df.shape[0]:,} registros com {df.shape[1]} variáveis")
    
    # Análise de tipos de dados
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    insights.append(f"- **Variáveis numéricas**: {len(numeric_cols)} colunas")
    insights.append(f"- **Variáveis categóricas**: {len(categorical_cols)} colunas")
    
    # Análise de valores faltantes
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        insights.append(f"\n### ⚠️ Dados Faltantes:")
        for col in missing_data[missing_data > 0].index:
            pct = (missing_data[col] / len(df)) * 100
            insights.append(f"- **{col}**: {missing_data[col]:,} valores ({pct:.2f}%)")
    else:
        insights.append(f"\n### ✅ **Qualidade dos Dados**: Não há valores faltantes")
    
    # Análise estatística
    if len(numeric_cols) > 0:
        insights.append(f"\n### 📈 Insights Estatísticos:")
        
        for col in numeric_cols[:5]:  # Limitar a 5 colunas mais importantes
            mean_val = df[col].mean()
            std_val = df[col].std()
            cv = (std_val / mean_val * 100) if mean_val != 0 else 0
            skew = df[col].skew()
            
            insights.append(f"\n**{col}:**")
            insights.append(f"- Média: {mean_val:.2f}, Desvio: {std_val:.2f}")
            
            if cv > 100:
                insights.append(f"- ⚠️ Alta variabilidade (CV: {cv:.1f}%)")
            elif cv > 50:
                insights.append(f"- Variabilidade moderada (CV: {cv:.1f}%)")
            else:
                insights.append(f"- Baixa variabilidade (CV: {cv:.1f}%)")
            
            if abs(skew) > 1:
                direction = "positiva" if skew > 0 else "negativa"
                insights.append(f"- Distribuição com forte assimetria {direction}")
    
    # Análise de correlações
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        high_corr = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
        
        if high_corr:
            insights.append(f"\n### 🔗 Correlações Importantes:")
            for col1, col2, corr in high_corr[:5]:  # Limitar a 5 correlações
                if corr > 0:
                    insights.append(f"- **{col1}** e **{col2}**: Forte correlação positiva ({corr:.2f})")
                else:
                    insights.append(f"- **{col1}** e **{col2}**: Forte correlação negativa ({corr:.2f})")
    
    # Análise de outliers
    outlier_info = _analyze_outliers(df, numeric_cols)
    if outlier_info:
        insights.append(f"\n### 🔍 Análise de Outliers:")
        for info in outlier_info[:5]:
            insights.append(f"- **{info['column']}**: {info['count']} outliers ({info['percentage']:.1f}% dos dados)")
    
    # Adicionar histórico de análises realizadas
    if 'messages' in st.session_state and len(st.session_state.messages) > 0:
        insights.append(f"\n### 📝 Análises Realizadas na Sessão:")
        analysis_count = _count_analyses(st.session_state.messages)
        
        for analysis, count in analysis_count.items():
            insights.append(f"- {analysis}: {count} análise(s)")
    
    # Recomendações finais
    insights.append(f"\n### 💡 Recomendações:")
    
    if len(numeric_cols) > 10:
        insights.append(f"- Dataset com muitas variáveis ({len(numeric_cols)}), considere análise de componentes principais (PCA)")
    
    if df.shape[0] > 100000:
        insights.append(f"- Grande volume de dados ({df.shape[0]:,} registros), considere técnicas de amostragem para análises exploratórias")
    
    if high_corr:
        insights.append(f"- Variáveis altamente correlacionadas detectadas, avalie multicolinearidade em modelos")
    
    if outlier_info and any(o['percentage'] > 5 for o in outlier_info):
        insights.append(f"- Presença significativa de outliers, considere técnicas de tratamento ou remoção")
    
    # Armazenar conclusões no histórico
    conclusion_summary = "\n".join(insights)
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    st.session_state.analysis_history.append({
        'timestamp': datetime.now().isoformat(),
        'type': 'conclusions',
        'content': conclusion_summary
    })
    
    return conclusion_summary


def _analyze_outliers(df: pd.DataFrame, numeric_cols) -> list:
    """Analisa outliers usando método IQR."""
    outlier_info = []
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
        outlier_count = len(outliers)
        
        if outlier_count > 0:
            outlier_info.append({
                'column': col,
                'count': outlier_count,
                'percentage': (outlier_count / len(df)) * 100
            })
    
    return sorted(outlier_info, key=lambda x: x['count'], reverse=True)


def _count_analyses(messages: list) -> dict:
    """Conta os tipos de análises realizadas."""
    analysis_count = {}
    
    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '').lower()
            
            if 'histogram' in content or 'histograma' in content:
                analysis_count['Histogramas'] = analysis_count.get('Histogramas', 0) + 1
            elif 'boxplot' in content:
                analysis_count['Boxplots'] = analysis_count.get('Boxplots', 0) + 1
            elif 'correlação' in content or 'correlation' in content:
                analysis_count['Correlações'] = analysis_count.get('Correlações', 0) + 1
            elif 'scatter' in content or 'dispersão' in content:
                analysis_count['Dispersões'] = analysis_count.get('Dispersões', 0) + 1
            elif 'estatística' in content or 'statistics' in content:
                analysis_count['Estatísticas'] = analysis_count.get('Estatísticas', 0) + 1
            elif 'visão geral' in content or 'overview' in content:
                analysis_count['Visões Gerais'] = analysis_count.get('Visões Gerais', 0) + 1
    
    return analysis_count
