"""
Componentes da interface do usuário.
"""

import streamlit as st
import pandas as pd
import logging
import traceback
from datetime import datetime

from agents import create_eda_agent

logger = logging.getLogger(__name__)


def initialize_session_state():
    """Inicializa as variáveis de estado da sessão."""
    if 'df' not in st.session_state:
        st.session_state.df = None
        logger.info("Initialized df in session_state")
    if 'agent_executor' not in st.session_state:
        st.session_state.agent_executor = None
        logger.info("Initialized agent_executor in session_state")
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        logger.info("Initialized chat_history in session_state")
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        logger.info("Initialized messages in session_state")
    if 'processing_steps' not in st.session_state:
        st.session_state.processing_steps = []
        logger.info("Initialized processing_steps in session_state")
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
        logger.info("Initialized analysis_history in session_state")
    if 'agent_memory' not in st.session_state:
        st.session_state.agent_memory = None
        logger.info("Initialized agent_memory in session_state")


def render_sidebar():
    """Renderiza a barra lateral com upload de arquivo e informações."""
    with st.sidebar:
        st.header("📁 Configuração de Dados")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Selecione um arquivo CSV",
            type=['csv'],
            help="Faça upload de um arquivo CSV para começar a análise"
        )
        
        # Seletor de LLM
        st.header("🤖 Seleção de Modelo")
        
        from config.settings_alternatives import alternative_settings
        
        # Obter lista de modelos gratuitos
        free_models = []
        model_info = {}
        
        for i, provider in enumerate(alternative_settings.get_fallback_configs()):
            if provider.get('is_free', False):
                display_name = f"{provider['name']}"
                if provider.get('rate_limit'):
                    display_name += f" ({provider['rate_limit']} req/dia)"
                else:
                    display_name += " (Ilimitado)"
                    
                free_models.append(display_name)
                model_info[display_name] = {
                    'index': i,
                    'name': provider['name'],
                    'model': provider['config']['model_name'],
                    'rate_limit': provider.get('rate_limit'),
                    'context': provider.get('context_length', 'N/A')
                }
        
        # Adicionar opção de fallback automático
        free_models.insert(0, "🔄 Fallback Automático (Recomendado)")
        model_info["🔄 Fallback Automático (Recomendado)"] = {
            'index': None,
            'name': 'Fallback Automático',
            'model': 'Múltiplos modelos',
            'rate_limit': 'Variável'
        }
        
        selected_model = st.selectbox(
            "Escolha o modelo LLM:",
            options=free_models,
            index=0,
            help="Selecione qual modelo usar para análise. O fallback automático tentará vários modelos em ordem de prioridade."
        )
        
        # Mostrar informações do modelo selecionado
        if selected_model in model_info:
            info = model_info[selected_model]
            with st.expander("ℹ️ Informações do Modelo", expanded=False):
                st.write(f"**Nome:** {info['name']}")
                st.write(f"**Modelo:** `{info['model']}`")
                st.write(f"**Rate Limit:** {info['rate_limit']}")
                if info.get('context'):
                    st.write(f"**Contexto:** {info['context']}")
        
        # Armazenar seleção no session_state
        st.session_state.selected_model_index = model_info[selected_model]['index']
        
        # Botão para aplicar mudança de modelo
        if st.button("🔄 Aplicar Modelo Selecionado", help="Reconfigura o agente com o modelo selecionado"):
            # Forçar recriação do agente
            st.session_state.agent_executor = None
            if hasattr(st.session_state, 'current_model_index'):
                del st.session_state.current_model_index
            st.rerun()
        
        if uploaded_file is not None:
            try:
                # Mostrar status de carregamento
                status_container = st.container()
                with status_container:
                    with st.spinner("📂 Carregando arquivo..."):
                        logger.info(f"Loading file: {uploaded_file.name}")
                        df = pd.read_csv(uploaded_file)
                        st.session_state.df = df
                        logger.info(f"File loaded successfully: {df.shape}")
                    
                    st.success(f"✅ Arquivo carregado: {df.shape[0]:,} linhas × {df.shape[1]} colunas")
                
                # Verificar se precisa recriar o agente (modelo mudou ou não existe)
                need_recreate = (
                    st.session_state.agent_executor is None or
                    not hasattr(st.session_state, 'current_model_index') or
                    st.session_state.current_model_index != st.session_state.selected_model_index
                )
                
                if need_recreate:
                    with status_container:
                        with st.spinner("🔧 Configurando agente de análise..."):
                            # IMPORTANTE: Garantir que o DataFrame está disponível antes de criar o agente
                            logger.info(f"Creating agent with DataFrame shape: {st.session_state.df.shape}")
                            
                            # Mostrar qual modelo será usado
                            if st.session_state.selected_model_index is not None:
                                from config.settings_alternatives import alternative_settings
                                selected_provider = alternative_settings.get_fallback_configs()[st.session_state.selected_model_index]
                                st.info(f"🎯 Configurando com {selected_provider['name']}...")
                            else:
                                st.info("🔄 Configurando com fallback automático...")
                            
                            # Recriar o agente (o DataFrame já está em st.session_state.df)
                            st.session_state.agent_executor = create_eda_agent()
                            
                            # Armazenar o índice do modelo atual
                            st.session_state.current_model_index = st.session_state.selected_model_index
                            
                            # Verificar se o DataFrame ainda está disponível após criar o agente
                            if st.session_state.df is not None:
                                logger.info(f"DataFrame verified after agent creation: {st.session_state.df.shape}")
                            else:
                                logger.error("DataFrame was lost after agent creation!")
                            
                            # Mostrar qual modelo foi realmente usado
                            from utils.llm_fallback import llm_fallback_manager
                            provider_info = llm_fallback_manager.get_current_provider_info()
                            if provider_info['name'] != 'Nenhum':
                                st.success(f"✅ Agente configurado com {provider_info['name']}!")
                            else:
                                st.success("✅ Agente configurado com sucesso!")
                            logger.info(f"Agent configured and ready with model index: {st.session_state.selected_model_index}")
                
                # Mostrar informações básicas
                st.markdown("### 📊 Dataset Carregado")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total de Linhas", f"{df.shape[0]:,}")
                with col2:
                    st.metric("Total de Colunas", df.shape[1])
                
                # Preview dos dados
                with st.expander("👀 Preview dos Dados", expanded=True):
                    tab1, tab2, tab3 = st.tabs(["Primeiras linhas", "Últimas linhas", "Amostra aleatória"])
                    with tab1:
                        st.dataframe(df.head(10))
                    with tab2:
                        st.dataframe(df.tail(10))
                    with tab3:
                        st.dataframe(df.sample(min(10, len(df))))
                
                # Mostrar colunas disponíveis
                with st.expander("📋 Colunas Disponíveis"):
                    cols_info = pd.DataFrame({
                        'Coluna': df.columns,
                        'Tipo': df.dtypes.astype(str),
                        'Não-Nulos': df.count()
                    })
                    st.dataframe(cols_info)
                
                # Mostrar status do modelo atual
                st.markdown("### 🤖 Status do Modelo")
                if st.session_state.agent_executor is not None:
                    from utils.llm_fallback import llm_fallback_manager
                    provider_info = llm_fallback_manager.get_current_provider_info()
                    
                    if provider_info['name'] != 'Nenhum':
                        st.info(f"**Modelo Ativo:** {provider_info['name']}")
                        st.caption(f"📋 {provider_info['model']}")
                        st.caption(f"💰 {'Gratuito' if provider_info.get('is_free') else 'Pago'}")
                        if provider_info.get('rate_limit'):
                            st.caption(f"⏱️ {provider_info['rate_limit']} req/dia")
                        
                        # Mostrar se está usando modelo selecionado ou fallback
                        if st.session_state.selected_model_index is not None:
                            st.caption("🎯 Modelo selecionado manualmente")
                        else:
                            st.caption("🔄 Fallback automático ativo")
                    else:
                        st.warning("⚠️ Nenhum modelo ativo")
                else:
                    st.warning("⚠️ Agente não configurado")
                    
            except Exception as e:
                logger.error(f"Error loading file: {e}")
                logger.error(traceback.format_exc())
                st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
                with st.expander("🔍 Detalhes do erro"):
                    st.code(traceback.format_exc())
                st.session_state.df = None
                st.session_state.agent_executor = None
        
        # Botão para limpar sessão
        if st.button("🔄 Nova Análise"):
            logger.info("Clearing session state")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_chat_interface():
    """Renderiza a interface de chat principal."""
    if st.session_state.df is not None and st.session_state.agent_executor is not None:
        
        # Container para mensagens do chat
        st.subheader("💬 Chat de Análise")
        
        # Exibir histórico de mensagens
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    # Para mensagens do assistente, verificar se há figuras
                    if "figure" in message:
                        st.plotly_chart(message["figure"], use_container_width=True)
                    else:
                        st.write(message["content"])
        
        # Input do usuário
        if prompt := st.chat_input("Digite sua pergunta sobre os dados..."):
            # Adicionar mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Processar com o agente
            _process_user_query(prompt)
    else:
        # Mensagem quando não há dados carregados
        st.info("👈 Por favor, faça upload de um arquivo CSV na barra lateral para começar a análise.")


def _process_user_query(prompt: str):
    """Processa a pergunta do usuário com o agente."""
    import io
    import sys
    import plotly.graph_objects as go
    from langchain_core.messages import HumanMessage, AIMessage
    from utils.callbacks import StreamlitCallbackHandler
    from utils.memory import save_to_history
    
    with st.chat_message("assistant"):
        # Container para mostrar progresso
        progress_container = st.container()
        result_container = st.container()
        
        with progress_container:
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            try:
                # Criar callback handler
                callback_handler = StreamlitCallbackHandler(progress_placeholder)
                
                # Status inicial
                status_placeholder.info("🔍 Processando sua pergunta...")
                logger.info(f"Processing user input: {prompt}")
                
                # Redirecionar stdout temporariamente para capturar prints
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                
                # Executar o agente com callbacks
                try:
                    result = st.session_state.agent_executor.invoke(
                        {"input": prompt},
                        {"callbacks": [callback_handler]}
                    )
                except (NotImplementedError, Exception) as nie:
                    # Verificar se é erro de rate limit
                    if "429" in str(nie) or "rate limit" in str(nie).lower():
                        logger.warning(f"Rate limit detected: {nie}")
                        st.error("⚠️ Limite de requisições excedido. Mudando para modo offline...")
                        
                        # Usar agente offline
                        from agents.offline_agent import offline_agent
                        result = offline_agent.invoke({"input": prompt})
                        
                    else:
                        # Outros erros - tentar sem memória
                        logger.warning(f"Memory issue detected: {nie}")
                        logger.info("Attempting without memory...")
                        
                        try:
                            # Tentar executar sem memória
                            result = st.session_state.agent_executor.invoke(
                                {"input": prompt, "chat_history": []},
                                {"callbacks": [callback_handler]}
                            )
                        except Exception as e2:
                            # Se ainda falhar, usar modo offline
                            logger.error(f"All attempts failed: {e2}")
                            st.error("❌ LLM indisponível. Usando modo offline...")
                            
                            from agents.offline_agent import offline_agent
                            result = offline_agent.invoke({"input": prompt})
                
                # Armazenar análise no histórico
                tools_used = [step[0].tool if hasattr(step[0], 'tool') else 'unknown' 
                            for step in result.get('intermediate_steps', [])]
                save_to_history(prompt, result.get('output', ''), tools_used)
                
                # Restaurar stdout
                verbose_output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Limpar status
                status_placeholder.empty()
                progress_placeholder.empty()
                
                logger.info("Agent processing completed successfully")
                
                # Processar o resultado
                with result_container:
                    output = result.get("output", "")
                    
                    # Log intermediate steps
                    if "intermediate_steps" in result:
                        num_steps = len(result['intermediate_steps'])
                        logger.info(f"Number of intermediate steps: {num_steps}")
                        
                        # ⚠️ ALERTA: Se o agente não usou ferramentas, avisar o usuário
                        if num_steps == 0:
                            logger.warning("Agent did not use any tools - response may not be based on actual data!")
                            st.warning("⚠️ **ATENÇÃO**: O agente respondeu sem consultar os dados. A resposta pode não estar baseada no arquivo carregado. Tente reformular sua pergunta de forma mais específica (ex: 'Analise os dados e mostre as estatísticas' ou 'Quais colunas existem no dataset?')")
                    
                    # Verificar se o resultado contém uma figura
                    if isinstance(output, go.Figure):
                        st.plotly_chart(output, use_container_width=True)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "figure": output
                        })
                    else:
                        # Verificar se alguma ferramenta retornou uma figura
                        figure_found = False
                        if "intermediate_steps" in result:
                            for step in result["intermediate_steps"]:
                                if len(step) > 1 and isinstance(step[1], go.Figure):
                                    st.plotly_chart(step[1], use_container_width=True)
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "figure": step[1]
                                    })
                                    figure_found = True
                                    break
                        
                        # Exibir texto de resposta com cabeçalho do modelo
                        if output:
                            # Obter informações do modelo atual
                            from utils.llm_fallback import llm_fallback_manager
                            provider_info = llm_fallback_manager.get_current_provider_info()
                            
                            # Criar cabeçalho com informações do modelo
                            model_header = f"""
                            ---
                            **🤖 Resposta gerada por:** {provider_info['name']}  
                            **📋 Modelo:** `{provider_info['model']}`  
                            **💰 Tipo:** {'Gratuito' if provider_info.get('is_free') else 'Pago'}  
                            **⏱️ Rate Limit:** {provider_info.get('rate_limit', 'N/A')} req/dia
                            ---
                            """
                            
                            # Exibir cabeçalho e resposta
                            st.markdown(model_header)
                            st.write(output)
                            
                            if not figure_found:
                                # Incluir cabeçalho na mensagem salva
                                full_response = model_header + "\n\n" + output
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": full_response
                                })
                
                # Atualizar histórico do chat
                st.session_state.chat_history.append(HumanMessage(content=prompt))
                st.session_state.chat_history.append(AIMessage(content=str(output)))
                
                # Mostrar detalhes do processamento
                with st.expander("🔍 Detalhes do Processamento"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📝 Log do Agente:**")
                        if verbose_output:
                            st.code(verbose_output, language="text")
                    
                    with col2:
                        st.markdown("**🔧 Ferramentas Utilizadas:**")
                        if "intermediate_steps" in result:
                            for i, step in enumerate(result["intermediate_steps"], 1):
                                if hasattr(step[0], 'tool'):
                                    st.write(f"{i}. {step[0].tool}")
                
            except Exception as e:
                status_placeholder.empty()
                progress_placeholder.empty()
                
                logger.error(f"Error processing question: {e}")
                logger.error(traceback.format_exc())
                
                st.error(f"❌ Erro ao processar pergunta: {str(e)}")
                
                with st.expander("🐛 Detalhes técnicos do erro"):
                    st.code(traceback.format_exc())
                    
                    # Mostrar informações de debug
                    st.markdown("**Informações de Debug:**")
                    st.write(f"- Pergunta: {prompt}")
                    st.write(f"- DataFrame carregado: {'Sim' if st.session_state.df is not None else 'Não'}")
                    st.write(f"- Agente configurado: {'Sim' if st.session_state.agent_executor is not None else 'Não'}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, verifique os detalhes acima."
                })


def render_suggestions():
    """Renderiza sugestões de perguntas organizadas por categoria."""
    with st.expander("💡 Sugestões de Perguntas", expanded=False):
        
        # NOVO: Seção de primeiros passos
        st.markdown("### 🚀 **Começando - Use Estas Perguntas Primeiro!**")
        st.info("""
        **Para garantir que o agente consulte seus dados:**
        
        ✅ "Analise os dados e me dê uma visão geral completa"  
        ✅ "Quais colunas existem no dataset?"  
        ✅ "Mostre as estatísticas descritivas de todas as colunas"  
        ✅ "Analise os dados e identifique os principais padrões"  
        
        ⚠️ **Evite perguntas muito genéricas** como "monte um plano" sem primeiro pedir para analisar os dados!
        """)
        
        st.markdown("---")
        
        # Primeira linha - Descrição dos Dados
        st.markdown("### 📋 **Descrição dos Dados**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Tipos e Estrutura:**
            - "Analise os dados e mostre os tipos de cada coluna"
            - "Me dê uma visão geral detalhada dos dados"
            - "Mostre a distribuição de cada variável"
            - "Crie histogramas das variáveis numéricas"
            """)
        
        with col2:
            st.markdown("""
            **Medidas Estatísticas:**
            - "Calcule estatísticas descritivas para todas as colunas"
            - "Qual o intervalo (mínimo e máximo) de cada variável?"
            - "Mostre média, mediana e desvio padrão dos dados"
            - "Analise a variabilidade dos dados"
            """)
        
        st.markdown("---")
        
        # Segunda linha - Padrões e Anomalias
        st.markdown("### 🔍 **Identificação de Padrões e Anomalias**")
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            **Padrões e Tendências:**
            - "Existem padrões ou tendências temporais?"
            - "Quais os valores mais frequentes ou menos frequentes?"
            - "Existem agrupamentos (clusters) nos dados?"
            - "Identifique padrões nos dados"
            """)
        
        with col4:
            st.markdown("""
            **Detecção de Outliers:**
            - "Existem valores atípicos nos dados?"
            - "Como esses outliers afetam a análise?"
            - "Crie um boxplot para identificar outliers"
            - "Mostre boxplots de todas as colunas"
            """)
        
        st.markdown("---")
        
        # Terceira linha - Relações e Conclusões
        st.markdown("### 🔗 **Relações entre Variáveis**")
        col5, col6 = st.columns(2)
        
        with col5:
            st.markdown("""
            **Análise de Correlações:**
            - "Como as variáveis estão relacionadas?"
            - "Existe correlação entre as variáveis?"
            - "Mostre a matriz de correlação"
            - "Faça gráficos de dispersão"
            - "Quais variáveis têm maior influência?"
            """)
        
        with col6:
            st.markdown("""
            **Insights e Conclusões:**
            - "Quais são suas conclusões sobre os dados?"
            - "Que insights você pode gerar?"
            - "O que você descobriu até agora?"
            - "Resuma as análises realizadas"
            - "Que recomendações você faria?"
            """)
        
        # Adicionar exemplos práticos
        st.markdown("---")
        st.markdown("### 💬 **Exemplos de Perguntas Compostas**")
        st.info("""
        **Análise Completa:**
        "Faça uma análise completa dos dados incluindo estatísticas, distribuições, outliers e correlações"
        
        **Análise Específica:**
        "Analise a variável 'Amount' mostrando sua distribuição, outliers e correlação com outras variáveis"
        
        **Investigação de Anomalias:**
        "Identifique e analise os outliers em todas as variáveis numéricas e sugira tratamento"
        """)


def render_history():
    """Renderiza o histórico de análises."""
    if 'analysis_history' in st.session_state and len(st.session_state.analysis_history) > 0:
        with st.expander(f"📜 Histórico de Análises ({len(st.session_state.analysis_history)} análises)"):
            for i, analysis in enumerate(reversed(st.session_state.analysis_history[-5:]), 1):
                st.markdown(f"**Análise {i}:**")
                # Verificar se 'query' existe no dicionário (compatibilidade)
                query_text = analysis.get('query', analysis.get('input', 'Pergunta não registrada'))
                if query_text and len(query_text) > 100:
                    st.write(f"- Pergunta: {query_text[:100]}...")
                else:
                    st.write(f"- Pergunta: {query_text}")
                    
                if analysis.get('tools_used'):
                    tools = analysis.get('tools_used', [])
                    if tools:
                        st.write(f"- Ferramentas: {', '.join(str(tool) for tool in tools)}")
                
                timestamp = analysis.get('timestamp', 'Não registrado')
                st.write(f"- Timestamp: {timestamp}")
                st.markdown("---")
