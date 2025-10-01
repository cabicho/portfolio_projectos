"""
Componente de Filtros do Dashboard
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

def create_filters_component():
    """Cria o componente de filtros"""
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Região", className="filter-label"),
                    dcc.Dropdown(
                        id='region-filter',
                        options=[
                            {'label': 'Todas as Regiões', 'value': 'all'},
                            {'label': 'Sudeste', 'value': 'southeast'},
                            {'label': 'Sul', 'value': 'south'},
                            {'label': 'Nordeste', 'value': 'northeast'},
                            {'label': 'Centro-Oeste', 'value': 'central_west'},
                            {'label': 'Norte', 'value': 'north'}
                        ],
                        value='all',
                        clearable=False
                    )
                ], width=3),
                
                dbc.Col([
                    html.Label("Tipo de Loja", className="filter-label"),
                    dcc.Dropdown(
                        id='store-type-filter',
                        options=[
                            {'label': 'Todos os Tipos', 'value': 'all'},
                            {'label': 'Shopping', 'value': 'shopping'},
                            {'label': 'Rua', 'value': 'street'},
                            {'label': 'Metrô', 'value': 'metro'}
                        ],
                        value='all',
                        clearable=False
                    )
                ], width=3),
                
                dbc.Col([
                    html.Label("Performance", className="filter-label"),
                    dcc.Dropdown(
                        id='performance-filter',
                        options=[
                            {'label': 'Todas', 'value': 'all'},
                            {'label': 'Alta Performance', 'value': 'high'},
                            {'label': 'Performance Média', 'value': 'medium'},
                            {'label': 'Baixa Performance', 'value': 'low'}
                        ],
                        value='all',
                        clearable=False
                    )
                ], width=3),
                
                dbc.Col([
                    html.Label("Período", className="filter-label"),
                    dcc.Dropdown(
                        id='period-filter',
                        options=[
                            {'label': '6 Semanas', 'value': '6weeks'},
                            {'label': '12 Semanas', 'value': '12weeks'},
                            {'label': 'Year to Date', 'value': 'ytd'}
                        ],
                        value='6weeks',
                        clearable=False
                    )
                ], width=3)
            ])
        ])
    ], className="mb-4")
