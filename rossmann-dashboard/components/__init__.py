"""
Componentes do Dashboard Rossmann
"""

from .kpi_cards import initialize_kpi_cards, register_kpi_callbacks
from .trend_chart import create_trend_chart, register_trend_callbacks
from .heat_map import create_heat_map, register_heatmap_callbacks
from .alerts_panel import create_alerts_panel, register_alerts_callbacks
from .comparison_table import create_comparison_table, register_comparison_callbacks
from .filters import create_filters_component

__all__ = [
    'initialize_kpi_cards',
    'create_trend_chart', 
    'create_heat_map',
    'create_alerts_panel',
    'create_comparison_table',
    'create_filters_component',
    'register_kpi_callbacks',
    'register_trend_callbacks',
    'register_heatmap_callbacks', 
    'register_alerts_callbacks',
    'register_comparison_callbacks'
]
