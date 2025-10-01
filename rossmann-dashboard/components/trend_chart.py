"""
Componente de Gráfico de Tendência
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from data.mock_data import generate_trend_data

def create_trend_chart():
    """Cria o componente do gráfico de tendência"""
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4("📈 Tendência de Faturamento - 6 Semanas", className="mb-0")
            ]),
            dbc.CardBody([
                dcc.Graph(
                    id="trend-chart",
                    config={'displayModeBar': True}
                )
            ])
        ])
    ])

def register_trend_callbacks(app):
    """Registra callbacks para o gráfico de tendência"""
    
    @app.callback(
        Output("trend-chart", "figure"),
        [Input("region-filter", "value"),
         Input("store-type-filter", "value"),
         Input("interval-component", "n_intervals")]
    )
    def update_trend_chart(region, store_type, n_intervals):
        """Atualiza o gráfico de tendência baseado nos filtros"""
        
        data = generate_trend_data()
        
        fig = go.Figure()
        
        # Previsão 2024
        fig.add_trace(go.Scatter(
            x=data['weeks'],
            y=data['forecast_2024'],
            mode='lines+markers',
            name='Previsão 2024',
            line=dict(color='#0066CC', width=3),
            marker=dict(size=8)
        ))
        
        # Histórico 2023
        fig.add_trace(go.Scatter(
            x=data['weeks'], 
            y=data['historical_2023'],
            mode='lines',
            name='Histórico 2023',
            line=dict(color='#FF6600', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Semanas",
            yaxis_title="Faturamento (R$ milhões)",
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=400
        )
        
        fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        
        return fig
