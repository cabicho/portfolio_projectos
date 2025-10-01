"""
Componente de Tabela Comparativa
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, dash_table
from data.mock_data import generate_comparison_data

def create_comparison_table():
    """Cria a tabela comparativa de performance"""
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4("🏆 Comparativo Loja vs Média Rede", className="mb-0")
            ]),
            dbc.CardBody([
                html.Div(id="comparison-table-container"),
                html.Div([
                    dbc.Badge("Top Performers", color="success", className="me-2"),
                    dbc.Badge("Em Atenção", color="warning", className="me-2"),
                    dbc.Badge("Crítico", color="danger")
                ], className="mt-3")
            ])
        ])
    ])

def register_comparison_callbacks(app):
    """Registra callbacks para a tabela comparativa"""
    
    @app.callback(
        Output("comparison-table-container", "children"),
        [Input("region-filter", "value"),
         Input("performance-filter", "value"),
         Input("interval-component", "n_intervals")]
    )
    def update_comparison_table(region, performance, n_intervals):
        """Atualiza a tabela comparativa"""
        
        data = generate_comparison_data()
        
        # Aplica filtros
        if region and region != "all":
            data = [item for item in data if item['region'] == region]
            
        if performance and performance != "all":
            if performance == "high":
                data = [item for item in data if item['vs_avg'] > 5]
            elif performance == "medium":
                data = [item for item in data if -5 <= item['vs_avg'] <= 5]
            elif performance == "low":
                data = [item for item in data if item['vs_avg'] < -5]
        
        # Cria a tabela
        columns = [
            {"name": "Loja", "id": "store"},
            {"name": "Região", "id": "region"},
            {"name": "vs Média", "id": "vs_avg_display"},
            {"name": "Faturamento", "id": "revenue"}
        ]
        
        return dash_table.DataTable(
            columns=columns,
            data=data,
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={
                'backgroundColor': '#0066CC',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{vs_avg} > 5'},
                    'backgroundColor': '#d4edda',
                    'color': '#155724'
                },
                {
                    'if': {'filter_query': '{vs_avg} < -5'},
                    'backgroundColor': '#f8d7da', 
                    'color': '#721c24'
                }
            ],
            page_size=10,
            sort_action='native'
        )
