"""
Ferramentas de visualização para o EDA Agent.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from langchain.tools import tool
from config.settings import settings

logger = logging.getLogger(__name__)

@tool
def plot_histogram(column: str) -> go.Figure:
    """
    Útil para visualizar a distribuição de uma única coluna numérica. 
    Retorna uma figura de histograma.
    """
    logger.info(f"Executing plot_histogram for column: {column}")
    logger.info(f"Session state has 'df': {'df' in st.session_state}")
    
    if 'df' not in st.session_state:
        logger.error("'df' key not found in session_state")
        return _create_error_figure("❌ Erro: Nenhum dado foi carregado ainda. Por favor, faça upload de um arquivo CSV.")
    
    if st.session_state.df is None:
        logger.error("DataFrame is None in session_state")
        return _create_error_figure("❌ Erro: O DataFrame está vazio. Por favor, faça upload de um arquivo CSV.")
    
    df = st.session_state.df
    logger.info(f"✅ Successfully accessed DataFrame with shape: {df.shape}")
    
    if column not in df.columns:
        logger.warning(f"Column {column} not found in DataFrame")
        return _create_error_figure(f"❌ Erro: A coluna '{column}' não existe no DataFrame.")
    
    if not pd.api.types.is_numeric_dtype(df[column]):
        return _create_error_figure(f"⚠️ A coluna '{column}' não é numérica.")
    
    # Criar histograma com Plotly
    fig = px.histogram(
        df, 
        x=column, 
        nbins=30,
        title=f"Distribuição de {column}",
        labels={column: column, 'count': 'Frequência'},
        color_discrete_sequence=[settings.VISUALIZATION_CONFIG["color_scheme"]]
    )
    
    # Adicionar estatísticas no gráfico
    mean_val = df[column].mean()
    median_val = df[column].median()
    
    fig.add_vline(
        x=mean_val, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Média: {mean_val:.2f}"
    )
    fig.add_vline(
        x=median_val, 
        line_dash="dash", 
        line_color="green",
        annotation_text=f"Mediana: {median_val:.2f}"
    )
    
    fig.update_layout(
        showlegend=False,
        height=settings.VISUALIZATION_CONFIG["default_height"],
        hovermode='x unified'
    )
    
    return fig


@tool
def plot_boxplot(column: str) -> go.Figure:
    """
    Gera um boxplot para uma coluna numérica, útil para identificar 
    outliers e a dispersão dos dados.
    """
    logger.info(f"Executing plot_boxplot for column: {column}")
    logger.info(f"Session state has 'df': {'df' in st.session_state}")
    
    if 'df' not in st.session_state:
        logger.error("'df' key not found in session_state")
        return _create_error_figure("❌ Erro: Nenhum dado foi carregado ainda. Por favor, faça upload de um arquivo CSV.")
    
    if st.session_state.df is None:
        logger.error("DataFrame is None in session_state")
        return _create_error_figure("❌ Erro: O DataFrame está vazio. Por favor, faça upload de um arquivo CSV.")
    
    df = st.session_state.df
    logger.info(f"✅ Successfully accessed DataFrame with shape: {df.shape}")
    
    if column not in df.columns:
        logger.warning(f"Column {column} not found in DataFrame")
        return _create_error_figure(f"❌ Erro: A coluna '{column}' não existe no DataFrame.")
    
    if not pd.api.types.is_numeric_dtype(df[column]):
        return _create_error_figure(f"⚠️ A coluna '{column}' não é numérica.")
    
    # Criar boxplot
    fig = go.Figure()
    fig.add_trace(go.Box(
        y=df[column],
        name=column,
        boxpoints='outliers',
        marker_color=settings.VISUALIZATION_CONFIG["color_scheme"],
        line_color=settings.VISUALIZATION_CONFIG["color_scheme"]
    ))
    
    fig.update_layout(
        title=f"Boxplot de {column}",
        yaxis_title=column,
        height=settings.VISUALIZATION_CONFIG["default_height"],
        showlegend=False
    )
    
    # Adicionar estatísticas
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    
    fig.add_annotation(
        text=f"IQR: {iqr:.2f}<br>Q1: {q1:.2f}<br>Q3: {q3:.2f}",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=10),
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1
    )
    
    return fig


@tool
def plot_multiple_boxplots() -> go.Figure:
    """
    Cria múltiplos boxplots para todas as colunas numéricas do dataset,
    útil para identificar outliers em todas as variáveis de uma só vez.
    """
    logger.info("Executing plot_multiple_boxplots for all numeric columns")
    logger.info(f"Session state has 'df': {'df' in st.session_state}")
    
    if 'df' not in st.session_state:
        logger.error("'df' key not found in session_state")
        return _create_error_figure("❌ Erro: Nenhum dado foi carregado ainda. Por favor, faça upload de um arquivo CSV.")
    
    if st.session_state.df is None:
        logger.error("DataFrame is None in session_state")
        return _create_error_figure("❌ Erro: O DataFrame está vazio. Por favor, faça upload de um arquivo CSV.")
    
    df = st.session_state.df
    logger.info(f"✅ Successfully accessed DataFrame with shape: {df.shape}")
    
    # Selecionar apenas colunas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        return _create_error_figure("⚠️ Não há colunas numéricas no DataFrame.")
    
    # Normalizar dados para melhor visualização
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    df_normalized = pd.DataFrame(
        scaler.fit_transform(df[numeric_cols]),
        columns=numeric_cols
    )
    
    max_cols = settings.VISUALIZATION_CONFIG["max_columns_boxplot"]
    subplot_max_cols = settings.VISUALIZATION_CONFIG["subplot_max_cols"]
    
    # Se muitas variáveis, criar um único boxplot com todas
    if len(numeric_cols) > 9:
        fig = go.Figure()
        
        # Adicionar um trace para cada coluna
        for col in numeric_cols[:max_cols]:
            fig.add_trace(go.Box(
                y=df_normalized[col],
                name=col,
                boxpoints='outliers',
                jitter=0.3,
                pointpos=-1.8
            ))
        
        fig.update_layout(
            title="Boxplots de Todas as Variáveis Numéricas (Normalizadas)",
            yaxis_title="Valores Normalizados (Z-score)",
            xaxis_title="Variáveis",
            height=600,
            showlegend=False,
            hovermode='x unified'
        )
        
        logger.info(f"Created combined boxplot for {min(max_cols, len(numeric_cols))} numeric columns")
        
    else:
        # Para poucas variáveis, criar subplots individuais
        n_cols = min(subplot_max_cols, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig = make_subplots(
            rows=n_rows, 
            cols=n_cols,
            subplot_titles=[col for col in numeric_cols],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        for idx, col in enumerate(numeric_cols):
            row = idx // n_cols + 1
            col_idx = idx % n_cols + 1
            
            fig.add_trace(
                go.Box(
                    y=df[col],
                    name=col,
                    boxpoints='outliers',
                    marker_color=settings.VISUALIZATION_CONFIG["color_scheme"]
                ),
                row=row,
                col=col_idx
            )
        
        fig.update_layout(
            title="Boxplots para Identificação de Outliers",
            height=300 * n_rows,
            showlegend=False
        )
        
        logger.info(f"Created {len(numeric_cols)} individual boxplots")
    
    # Adicionar anotação com resumo de outliers
    _add_outlier_summary(fig, df, numeric_cols[:max_cols])
    
    return fig


@tool
def plot_correlation_heatmap() -> go.Figure:
    """
    Cria um heatmap de correlação para visualizar a relação entre 
    todas as colunas numéricas do DataFrame.
    """
    logger.info("Executing plot_correlation_heatmap")
    logger.info(f"Session state has 'df': {'df' in st.session_state}")
    
    if 'df' not in st.session_state:
        logger.error("'df' key not found in session_state")
        return _create_error_figure("❌ Erro: Nenhum dado foi carregado ainda. Por favor, faça upload de um arquivo CSV.")
    
    if st.session_state.df is None:
        logger.error("DataFrame is None in session_state")
        return _create_error_figure("❌ Erro: O DataFrame está vazio. Por favor, faça upload de um arquivo CSV.")
    
    df = st.session_state.df
    logger.info(f"✅ Successfully accessed DataFrame with shape: {df.shape}")
    
    # Selecionar apenas colunas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) < 2:
        return _create_error_figure("⚠️ Necessário pelo menos 2 colunas numéricas para calcular correlação.")
    
    # Calcular matriz de correlação
    corr_matrix = df[numeric_cols].corr()
    
    # Criar heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlação")
    ))
    
    fig.update_layout(
        title="Matriz de Correlação",
        height=600,
        width=800,
        xaxis_title="",
        yaxis_title="",
        xaxis={'side': 'bottom'}
    )
    
    return fig


@tool
def plot_scatter(x_column: str, y_column: str) -> go.Figure:
    """
    Gera um gráfico de dispersão (scatter plot) para investigar 
    a relação entre duas colunas numéricas específicas.
    """
    logger.info(f"Executing plot_scatter for columns: {x_column} vs {y_column}")
    logger.info(f"Session state has 'df': {'df' in st.session_state}")
    
    if 'df' not in st.session_state:
        logger.error("'df' key not found in session_state")
        return _create_error_figure("❌ Erro: Nenhum dado foi carregado ainda. Por favor, faça upload de um arquivo CSV.")
    
    if st.session_state.df is None:
        logger.error("DataFrame is None in session_state")
        return _create_error_figure("❌ Erro: O DataFrame está vazio. Por favor, faça upload de um arquivo CSV.")
    
    df = st.session_state.df
    logger.info(f"✅ Successfully accessed DataFrame with shape: {df.shape}")
    
    # Validação das colunas
    missing_cols = []
    if x_column not in df.columns:
        missing_cols.append(x_column)
    if y_column not in df.columns:
        missing_cols.append(y_column)
    
    if missing_cols:
        return _create_error_figure(f"❌ Erro: Coluna(s) não encontrada(s): {', '.join(missing_cols)}")
    
    # Verificar se as colunas são numéricas
    non_numeric = []
    if not pd.api.types.is_numeric_dtype(df[x_column]):
        non_numeric.append(x_column)
    if not pd.api.types.is_numeric_dtype(df[y_column]):
        non_numeric.append(y_column)
    
    if non_numeric:
        return _create_error_figure(f"⚠️ Coluna(s) não numérica(s): {', '.join(non_numeric)}")
    
    # Criar scatter plot
    fig = px.scatter(
        df, 
        x=x_column, 
        y=y_column,
        title=f"Relação entre {x_column} e {y_column}",
        trendline="ols",  # Adicionar linha de tendência
        color_discrete_sequence=[settings.VISUALIZATION_CONFIG["color_scheme"]]
    )
    
    # Calcular correlação
    correlation = df[x_column].corr(df[y_column])
    
    fig.add_annotation(
        text=f"Correlação: {correlation:.3f}",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=12),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1
    )
    
    fig.update_layout(
        height=settings.VISUALIZATION_CONFIG["default_height"],
        hovermode='closest'
    )
    
    return fig


# Funções auxiliares privadas
def _create_error_figure(message: str) -> go.Figure:
    """Cria uma figura com mensagem de erro."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14)
    )
    fig.update_layout(
        title="Erro",
        height=400
    )
    return fig


def _add_outlier_summary(fig: go.Figure, df: pd.DataFrame, columns) -> None:
    """Adiciona resumo de outliers ao gráfico."""
    outlier_summary = []
    
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col].count()
        if outliers > 0:
            outlier_summary.append(f"{col}: {outliers} outliers")
    
    if outlier_summary:
        summary_text = "Outliers detectados: " + ", ".join(outlier_summary[:5])
        if len(outlier_summary) > 5:
            summary_text += f" e mais {len(outlier_summary) - 5} variáveis"
        
        fig.add_annotation(
            text=summary_text,
            xref="paper", yref="paper",
            x=0.02, y=-0.05,
            showarrow=False,
            font=dict(size=10),
            align="left"
        )
