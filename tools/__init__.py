"""
Ferramentas de análise para o EDA Agent.
"""

from .data_analysis import (
    get_data_description,
    get_descriptive_statistics
)

from .visualizations import (
    plot_histogram,
    plot_boxplot,
    plot_multiple_boxplots,
    plot_correlation_heatmap,
    plot_scatter
)

from .insights import generate_insights_and_conclusions

# Lista de todas as ferramentas disponíveis
ALL_TOOLS = [
    get_data_description,
    get_descriptive_statistics,
    plot_histogram,
    plot_boxplot,
    plot_multiple_boxplots,
    plot_correlation_heatmap,
    plot_scatter,
    generate_insights_and_conclusions
]

__all__ = [
    'get_data_description',
    'get_descriptive_statistics',
    'plot_histogram',
    'plot_boxplot',
    'plot_multiple_boxplots',
    'plot_correlation_heatmap',
    'plot_scatter',
    'generate_insights_and_conclusions',
    'ALL_TOOLS'
]
