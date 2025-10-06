"""
Agente offline para quando LLMs não estão disponíveis.
"""

import logging
import streamlit as st
from typing import Dict, Any
from tools import ALL_TOOLS

logger = logging.getLogger(__name__)

class OfflineAgent:
    """Agente que funciona sem LLM, usando regras pré-definidas."""
    
    def __init__(self):
        """Inicializa o agente offline."""
        self.tools = {tool.name: tool for tool in ALL_TOOLS}
        self.keyword_tool_mapping = {
            # Mapeamento de palavras-chave para ferramentas
            
            # Descrição dos dados
            'visão geral': 'get_data_description',
            'overview': 'get_data_description',
            'descrição': 'get_data_description',
            'info': 'get_data_description',
            'tipos de dados': 'get_data_description',
            'numéricos': 'get_data_description',
            'categóricos': 'get_data_description',
            
            # Estatísticas
            'estatística': 'get_descriptive_statistics',
            'statistics': 'get_descriptive_statistics',
            'média': 'get_descriptive_statistics',
            'mediana': 'get_descriptive_statistics',
            'desvio': 'get_descriptive_statistics',
            'variância': 'get_descriptive_statistics',
            'tendência central': 'get_descriptive_statistics',
            'variabilidade': 'get_descriptive_statistics',
            'mínimo': 'get_descriptive_statistics',
            'máximo': 'get_descriptive_statistics',
            'intervalo': 'get_descriptive_statistics',
            
            # Distribuições
            'histograma': 'plot_histogram',
            'histogram': 'plot_histogram',
            'distribuição': 'plot_histogram',
            'distribution': 'plot_histogram',
            'frequentes': 'plot_histogram',
            'frequência': 'plot_histogram',
            
            # Outliers
            'boxplot': 'plot_boxplot',
            'outlier': 'plot_boxplot',
            'outliers': 'plot_multiple_boxplots',
            'atípicos': 'plot_multiple_boxplots',
            'anomalias': 'plot_multiple_boxplots',
            'todos': 'plot_multiple_boxplots',
            'todas': 'plot_multiple_boxplots',
            
            # Correlações
            'correlação': 'plot_correlation_heatmap',
            'correlation': 'plot_correlation_heatmap',
            'heatmap': 'plot_correlation_heatmap',
            'relacionadas': 'plot_correlation_heatmap',
            'influência': 'plot_correlation_heatmap',
            
            # Scatter
            'scatter': 'plot_scatter',
            'dispersão': 'plot_scatter',
            'relação': 'plot_scatter',
            'versus': 'plot_scatter',
            
            # Insights
            'conclusão': 'generate_insights_and_conclusions',
            'conclusões': 'generate_insights_and_conclusions',
            'insights': 'generate_insights_and_conclusions',
            'resumo': 'generate_insights_and_conclusions',
            'padrões': 'generate_insights_and_conclusions',
            'tendências': 'generate_insights_and_conclusions',
            'clusters': 'generate_insights_and_conclusions',
            'agrupamentos': 'generate_insights_and_conclusions',
            'descobertas': 'generate_insights_and_conclusions',
            'recomendações': 'generate_insights_and_conclusions'
        }
    
    def invoke(self, inputs: Dict[str, Any], callbacks=None) -> Dict[str, Any]:
        """
        Processa uma pergunta usando lógica baseada em regras.
        
        Args:
            inputs: Dicionário com 'input' contendo a pergunta
            callbacks: Callbacks opcionais
            
        Returns:
            Dicionário com 'output' contendo a resposta
        """
        query = inputs.get('input', '').lower()
        logger.info(f"Offline agent processing: {query}")
        
        # Tentar identificar a ferramenta apropriada
        tool_name = self._identify_tool(query)
        
        if tool_name:
            # Executar a ferramenta
            tool = self.tools[tool_name]
            
            # Extrair parâmetros se necessário
            params = self._extract_parameters(query, tool_name)
            
            try:
                # Executar ferramenta
                logger.info(f"Executing tool: {tool_name} with params: {params}")
                result = tool.func(**params)
                
                # Formatar a resposta de forma amigável
                formatted_output = self._format_response(tool_name, result, params)
                
                # Preparar resposta
                response = {
                    'output': formatted_output,
                    'intermediate_steps': [(MockAction(tool_name), result)]
                }
                
                # Adicionar mensagem explicativa
                if hasattr(st, 'warning'):
                    st.warning("🤖 Modo Offline: Usando análise baseada em regras (LLM indisponível)")
                
                return response
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                return {
                    'output': f"Erro ao executar {tool_name}: {str(e)}",
                    'intermediate_steps': []
                }
        else:
            # Não conseguiu identificar ferramenta
            return self._suggest_options()
    
    def _identify_tool(self, query: str) -> str:
        """Identifica qual ferramenta usar baseado em palavras-chave e contexto."""
        query_lower = query.lower()
        
        # Palavras que indicam análise de TODAS as colunas
        all_indicators = ['todas', 'todos', 'all', 'cada', 'completo', 'completa', 
                          'geral', 'overview', 'múltiplos', 'múltiplas', 'conjunto']
        
        # Verifica se há coluna específica mencionada
        specific_column = None
        if 'df' in st.session_state and st.session_state.df is not None:
            df = st.session_state.df
            for col in df.columns:
                if col.lower() in query_lower:
                    specific_column = col
                    break
        
        # 1. VISÃO GERAL / DESCRIÇÃO
        if any(word in query_lower for word in ['visão geral', 'overview', 'descrição', 'descrever', 
                                                 'tipos de dados', 'info', 'informações']):
            return 'get_data_description'
        
        # 2. ESTATÍSTICAS DESCRITIVAS
        if any(word in query_lower for word in ['estatística', 'statistics', 'média', 'mediana', 
                                                 'desvio', 'variância', 'mínimo', 'máximo', 
                                                 'tendência central', 'variabilidade', 'intervalo']):
            # Se menciona "todas" ou não especifica coluna, analisar todas
            if any(word in query_lower for word in all_indicators) or not specific_column:
                return 'get_descriptive_statistics'
            # Se menciona coluna específica
            elif specific_column:
                return 'get_descriptive_statistics'
            else:
                return 'get_descriptive_statistics'
        
        # 3. HISTOGRAMA / DISTRIBUIÇÃO
        if any(word in query_lower for word in ['histograma', 'histogram', 'distribuição', 
                                                 'distribution', 'frequência']):
            # Histograma sempre precisa de coluna específica
            if specific_column:
                return 'plot_histogram'
            # Se não há coluna, sugerir estatísticas descritivas
            return 'get_descriptive_statistics'
        
        # 4. BOXPLOT / OUTLIERS
        if any(word in query_lower for word in ['boxplot', 'box plot', 'outlier', 'outliers', 
                                                 'atípicos', 'anomalias']):
            # Se menciona "todas" ou não especifica coluna
            if any(word in query_lower for word in all_indicators) or not specific_column:
                return 'plot_multiple_boxplots'
            # Se menciona coluna específica
            elif specific_column:
                return 'plot_boxplot'
            else:
                # Por padrão, mostrar todas para análise de outliers
                return 'plot_multiple_boxplots'
        
        # 5. CORRELAÇÃO / RELACIONAMENTO
        if any(word in query_lower for word in ['correlação', 'correlation', 'heatmap', 
                                                 'relacionadas', 'relacionamento', 'influência']):
            return 'plot_correlation_heatmap'
        
        # 6. SCATTER / DISPERSÃO
        if any(word in query_lower for word in ['scatter', 'dispersão', 'versus', 'vs', 
                                                 'relação entre', 'comparar']):
            # Scatter precisa de duas colunas
            return 'plot_scatter'
        
        # 7. INSIGHTS / CONCLUSÕES
        if any(word in query_lower for word in ['conclusão', 'conclusões', 'insights', 'resumo',
                                                 'padrões', 'tendências', 'descobertas', 
                                                 'recomendações', 'análise completa', 'sintetizar']):
            return 'generate_insights_and_conclusions'
        
        # 8. PALAVRAS-CHAVE ESPECÍFICAS DE ANÁLISE
        if any(word in query_lower for word in ['valores únicos', 'nulos', 'missing', 'faltantes']):
            return 'get_data_description'
        
        if any(word in query_lower for word in ['clusters', 'agrupamentos', 'grupos']):
            return 'generate_insights_and_conclusions'
        
        # 9. FALLBACK: Tentar identificar baseado em contexto geral
        if any(word in query_lower for word in ['analisar', 'análise', 'mostrar', 'exibir']):
            # Se tem coluna específica
            if specific_column:
                # Decidir baseado em outras palavras
                if 'distribui' in query_lower:
                    return 'plot_histogram'
                else:
                    return 'get_descriptive_statistics'
            # Se não tem coluna, visão geral
            else:
                return 'get_data_description'
        
        return None
    
    def _extract_parameters(self, query: str, tool_name: str) -> Dict[str, Any]:
        """Extrai parâmetros da query para a ferramenta com inteligência contextual."""
        params = {}
        query_lower = query.lower()
        
        # Ferramentas que NÃO precisam de parâmetros
        if tool_name in ['plot_multiple_boxplots', 'plot_correlation_heatmap', 
                         'get_data_description', 'generate_insights_and_conclusions']:
            return params
        
        # Obter DataFrame se disponível
        df = None
        if 'df' in st.session_state and st.session_state.df is not None:
            df = st.session_state.df
        
        # 1. FERRAMENTAS QUE PRECISAM DE UMA COLUNA
        if tool_name in ['plot_histogram', 'plot_boxplot']:
            if df is not None:
                # Procurar nome de coluna na query
                for col in df.columns:
                    # Verificação exata (case insensitive)
                    if col.lower() in query_lower:
                        params['column'] = col
                        return params
                    # Verificação parcial para colunas com underscore ou hífen
                    col_parts = col.replace('_', ' ').replace('-', ' ').lower()
                    if col_parts in query_lower:
                        params['column'] = col
                        return params
                
                # Se não encontrou coluna mas é histograma/boxplot, pegar primeira numérica
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    params['column'] = numeric_cols[0]
        
        # 2. ESTATÍSTICAS DESCRITIVAS (opcional column)
        elif tool_name == 'get_descriptive_statistics':
            if df is not None:
                # Verificar se menciona coluna específica
                for col in df.columns:
                    if col.lower() in query_lower:
                        params['column'] = col
                        return params
                # Se não especifica, retorna sem parâmetro (analisará todas)
                return params
        
        # 3. SCATTER PLOT (precisa de 2 colunas)
        elif tool_name == 'plot_scatter':
            if df is not None:
                cols_found = []
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                # Procurar colunas mencionadas
                for col in numeric_cols:
                    if col.lower() in query_lower:
                        cols_found.append(col)
                
                # Procurar palavras-chave especiais
                if 'versus' in query_lower or ' vs ' in query_lower or ' x ' in query_lower:
                    # Tentar extrair padrão "A versus B" ou "A vs B"
                    import re
                    patterns = [
                        r'(\w+)\s+versus\s+(\w+)',
                        r'(\w+)\s+vs\s+(\w+)',
                        r'(\w+)\s+x\s+(\w+)',
                        r'entre\s+(\w+)\s+e\s+(\w+)'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, query_lower)
                        if match:
                            col1, col2 = match.groups()
                            # Verificar se são colunas válidas
                            valid_cols = []
                            for col_name in [col1, col2]:
                                for actual_col in numeric_cols:
                                    if col_name in actual_col.lower():
                                        valid_cols.append(actual_col)
                                        break
                            
                            if len(valid_cols) == 2:
                                params['x_column'] = valid_cols[0]
                                params['y_column'] = valid_cols[1]
                                return params
                
                # Se encontrou 2+ colunas, usar as primeiras duas
                if len(cols_found) >= 2:
                    params['x_column'] = cols_found[0]
                    params['y_column'] = cols_found[1]
                # Se encontrou apenas 1, procurar correlação mais forte
                elif len(cols_found) == 1:
                    # Pegar coluna com maior correlação
                    corr_matrix = df[numeric_cols].corr()
                    col_corrs = corr_matrix[cols_found[0]].abs().sort_values(ascending=False)
                    # Pegar segunda maior (primeira é consigo mesma)
                    if len(col_corrs) > 1:
                        params['x_column'] = cols_found[0]
                        params['y_column'] = col_corrs.index[1]
                # Se não encontrou nenhuma, usar as duas primeiras numéricas
                elif len(numeric_cols) >= 2:
                    params['x_column'] = numeric_cols[0]
                    params['y_column'] = numeric_cols[1]
        
        return params
    
    def _format_response(self, tool_name: str, result, params: Dict[str, Any]) -> str:
        """
        Formata a resposta da ferramenta de forma amigável.
        
        Args:
            tool_name: Nome da ferramenta executada
            result: Resultado da ferramenta
            params: Parâmetros usados
            
        Returns:
            Resposta formatada em string
        """
        import plotly.graph_objects as go
        
        # Se o resultado é uma figura Plotly, retornar como está
        if isinstance(result, go.Figure):
            return result
        
        # Formatação específica por ferramenta
        formatted = f"## 📊 Resultado da Análise\n\n"
        
        if tool_name == 'get_data_description':
            formatted += "### Visão Geral do Dataset\n\n"
            formatted += str(result)
            
        elif tool_name == 'get_descriptive_statistics':
            formatted += "### Estatísticas Descritivas\n\n"
            if params.get('column'):
                formatted += f"**Análise da coluna:** `{params['column']}`\n\n"
            else:
                formatted += "**Análise de todas as colunas numéricas**\n\n"
            
            # Processar o resultado para melhor formatação
            if isinstance(result, str):
                # Se já é string, adicionar formatação markdown
                lines = result.split('\n')
                formatted_lines = []
                
                for line in lines:
                    # Destacar títulos
                    if '**' in line or '📈' in line or '📊' in line:
                        formatted_lines.append(line)
                    # Formatar tabelas de dados
                    elif any(stat in line.lower() for stat in ['count', 'mean', 'std', 'min', 'max', '25%', '50%', '75%']):
                        # Adicionar formatação de código para tabelas
                        if not line.strip().startswith('```'):
                            formatted_lines.append(f"```\n{line}")
                        else:
                            formatted_lines.append(line)
                    else:
                        formatted_lines.append(line)
                
                # Garantir que blocos de código sejam fechados
                result_text = '\n'.join(formatted_lines)
                if '```' in result_text and result_text.count('```') % 2 != 0:
                    result_text += '\n```'
                    
                formatted += result_text
            else:
                formatted += str(result)
                
        elif tool_name == 'generate_insights_and_conclusions':
            formatted = str(result)  # Já vem bem formatado
            
        elif tool_name in ['plot_histogram', 'plot_boxplot', 'plot_multiple_boxplots', 
                          'plot_correlation_heatmap', 'plot_scatter']:
            # Para visualizações, adicionar contexto
            formatted += f"### Visualização: {tool_name.replace('plot_', '').replace('_', ' ').title()}\n\n"
            
            if params:
                formatted += "**Parâmetros utilizados:**\n"
                for key, value in params.items():
                    formatted += f"- {key}: `{value}`\n"
                formatted += "\n"
            
            # Retornar a figura diretamente
            return result
            
        else:
            # Fallback genérico
            formatted += str(result)
        
        # Adicionar rodapé informativo
        formatted += "\n\n---\n"
        formatted += "*📝 Análise realizada em modo offline (sem IA). "
        formatted += "Para análises mais sofisticadas, configure um modelo de linguagem.*"
        
        return formatted
    
    def _suggest_options(self) -> Dict[str, Any]:
        """Retorna sugestões quando não consegue processar."""
        suggestions = """
## 🤖 **Modo Offline Ativo** (LLM indisponível)

Não consegui identificar qual análise você deseja. Por favor, seja mais específico.

### 📊 **Análises Disponíveis:**

**Descrição dos Dados:**
- `"visão geral dos dados"` - Informações gerais sobre o dataset
- `"tipos de dados"` - Tipos de cada coluna

**Estatísticas:**
- `"estatísticas descritivas"` - Estatísticas de todas as colunas
- `"estatísticas da coluna [nome]"` - Estatísticas de uma coluna específica
- `"média e desvio padrão"` - Medidas de tendência central

**Visualizações:**
- `"histograma da coluna [nome]"` - Distribuição de uma variável
- `"boxplot da coluna [nome]"` - Análise de outliers de uma coluna
- `"boxplot de todas as colunas"` - Outliers de todas as variáveis
- `"matriz de correlação"` - Correlações entre variáveis
- `"gráfico de dispersão entre [col1] e [col2]"` - Relação entre duas variáveis

**Insights:**
- `"gerar conclusões"` - Análise completa com insights

### 💡 **Exemplos de Uso:**
```
"mostre as estatísticas da coluna Amount"
"crie um histograma da coluna V1"
"análise de outliers em todas as colunas"
"qual a correlação entre as variáveis?"
```

### ⚠️ **Dica:**
Mencione o nome exato das colunas do seu dataset para melhores resultados.
        """
        
        return {
            'output': suggestions,
            'intermediate_steps': []
        }

class MockAction:
    """Classe mock para simular ação do agente."""
    def __init__(self, tool_name):
        self.tool = tool_name

# Instância global
offline_agent = OfflineAgent()
