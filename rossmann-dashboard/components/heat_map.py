"""
Componente de Mapa de Calor por Região
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from data.mock_data import generate_heatmap_data

def create_heat_map():
    """Cria o componente do mapa de calor"""
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4("🗺️ Mapa de Calor - Elegibilidade por Região", className="mb-0")
            ]),
            dbc.CardBody([
                dcc.Graph(
                    id="heat-map",
                    config={'displayModeBar': True}
                )
            ])
        ])
    ])

def register_heatmap_callbacks(app):
    """Registra callbacks para o mapa de calor"""
    
    @app.callback(
        Output("heat-map", "figure"),
        [Input("interval-component", "n_intervals")]
    )
    def update_heat_map(n_intervals):
        """Atualiza o mapa de calor"""
        
        data = generate_heatmap_data()
        
        # Criar um gráfico simples de barras como fallback
        # já que o choropleth pode ter problemas de dependência
        fig = go.Figure(data=[
            go.Bar(
                x=data['region_names'],
                y=data['z_values'],
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            )
        ])
        
        fig.update_layout(
            title="Elegibilidade por Região",
            xaxis_title="Região",
            yaxis_title="% Elegibilidade",
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400
        )
        
        return fig
