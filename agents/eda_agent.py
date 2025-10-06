"""
Configuração do agente de análise exploratória de dados.
"""

import logging
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config.settings import settings
from tools import ALL_TOOLS
from utils.memory import create_memory

logger = logging.getLogger(__name__)

# Template do sistema especializado em análise de dados
SYSTEM_PROMPT = """Você é um especialista sênior em análise exploratória de dados e ciência de dados.
Sua função é ajudar o usuário a entender profundamente os dados, identificar padrões e gerar insights acionáveis.

⚠️ REGRA CRÍTICA - NUNCA IGNORE ISSO:
Você DEVE SEMPRE usar as ferramentas disponíveis para acessar e analisar os dados reais antes de responder.
NUNCA responda baseado em suposições ou conhecimento geral - SEMPRE consulte os dados primeiro usando as ferramentas.

📋 FLUXO OBRIGATÓRIO PARA QUALQUER PERGUNTA:
1. PRIMEIRO: Use get_data_description() para entender o dataset
2. SEGUNDO: Use as ferramentas apropriadas para analisar os dados específicos da pergunta
3. TERCEIRO: Baseie sua resposta APENAS nos resultados obtidos das ferramentas
4. NUNCA responda sem ter usado pelo menos uma ferramenta

FERRAMENTAS DISPONÍVEIS (USE-AS!):
- get_data_description: Visão geral completa do dataset (USE PRIMEIRO!)
- get_descriptive_statistics: Estatísticas descritivas detalhadas de colunas
- plot_histogram: Visualização de distribuições de uma coluna
- plot_boxplot: Identificação de outliers para UMA coluna específica
- plot_multiple_boxplots: Boxplots de TODAS as colunas numéricas de uma vez
- plot_correlation_heatmap: Análise de correlações entre variáveis
- plot_scatter: Investigação de relações entre duas variáveis
- generate_insights_and_conclusions: Sintetiza todas as análises em conclusões

EXEMPLOS DE COMO PROCEDER:

Pergunta: "Quais os principais feedbacks?"
✅ CORRETO:
1. Usar get_data_description() para ver as colunas disponíveis
2. Usar get_descriptive_statistics() nas colunas de feedback
3. Responder baseado nos dados reais

❌ ERRADO:
1. Responder diretamente sem usar ferramentas

Pergunta: "Monte um plano de ação"
✅ CORRETO:
1. Usar get_data_description() para entender os dados
2. Usar get_descriptive_statistics() em colunas relevantes
3. Analisar padrões nos dados reais
4. Criar plano baseado nos insights dos dados

❌ ERRADO:
1. Criar plano genérico sem consultar os dados

REGRAS IMPORTANTES:
- Cada análise deve contribuir para um entendimento maior dos dados REAIS
- Você tem memória das últimas {window_size} interações para manter contexto
- Quando perguntado sobre conclusões, use generate_insights_and_conclusions
- Quando solicitado boxplots de TODAS as colunas, use plot_multiple_boxplots
- Quando solicitado boxplot de UMA coluna específica, use plot_boxplot
- Seja proativo em identificar próximas análises relevantes baseadas em descobertas anteriores
- Sempre forneça interpretações contextualizadas dos resultados REAIS dos dados
- SE NÃO SOUBER QUAIS COLUNAS EXISTEM, use get_data_description() PRIMEIRO!
""".format(window_size=settings.MEMORY_CONFIG["window_size"])


def create_eda_agent() -> AgentExecutor:
    """
    Cria o agente LangChain para análise exploratória de dados com memória.
    
    Returns:
        AgentExecutor: Executor do agente configurado
    """
    logger.info("Creating EDA agent with memory...")
    
    # Configurar o LLM com sistema de fallback
    try:
        # Tentar usar o fallback manager primeiro
        from utils.llm_fallback import llm_fallback_manager
        
        # Verificar se há um modelo específico selecionado pelo usuário
        force_provider = None
        if hasattr(st.session_state, 'selected_model_index') and st.session_state.selected_model_index is not None:
            force_provider = st.session_state.selected_model_index
            logger.info(f"Using user-selected model at index: {force_provider}")
        
        llm = llm_fallback_manager.get_llm(force_provider=force_provider)
        logger.info("LLM configured with fallback system")
    except Exception as e:
        logger.warning(f"Fallback system error: {e}")
        # Tentar usar configuração padrão
        try:
            from config.settings import get_llm_config
            llm_config = get_llm_config()
            llm = ChatOpenAI(**llm_config)
            logger.info("LLM configured with default settings")
        except Exception as e2:
            logger.error(f"Error configuring LLM: {e2}")
            # Se tudo falhar, levantar exceção para trigger do offline mode
            raise ValueError(f"LLM indisponível: {e2}")
    
    # Configurar memória de conversação
    memory = create_memory(llm)
    
    # Criar o prompt template para o agente
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Criar o agente
    try:
        agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
        logger.info("Agent created successfully")
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise
    
    # Criar o executor do agente com memória
    try:
        agent_executor = AgentExecutor(
            agent=agent,
            tools=ALL_TOOLS,
            memory=memory if memory else None,
            **settings.AGENT_CONFIG
        )
        logger.info("Agent executor created successfully with memory")
        
        # Armazenar o executor com memória no session_state
        st.session_state.agent_memory = memory
        
    except Exception as e:
        logger.error(f"Error creating agent executor: {e}")
        raise
    
    logger.info("EDA agent setup completed")
    return agent_executor
