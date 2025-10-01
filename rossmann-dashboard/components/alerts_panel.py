"""
Componente de Painel de Alertas
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
from data.mock_data import generate_alerts_data

def create_alert_item(alert):
    """Cria um item individual de alerta"""
    
    alert_colors = {
        'critical': 'danger',
        'warning': 'warning', 
        'info': 'info'
    }
    
    alert_icons = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': '💡'
    }
    
    return dbc.Alert([
        html.Div([
            html.Span(alert_icons[alert['type']], className="alert-icon"),
            html.Strong(alert['store'], className="alert-store"),
            html.P(alert['message'], className="alert-message mb-1"),
            html.Small([
                html.Span(alert['time'], className="alert-time"),
                " • ",
                html.Strong("Ação: ", className="text-muted"),
                alert['action']
            ], className="alert-details")
        ])
    ], color=alert_colors[alert['type']], className="alert-item")

def create_alerts_panel():
    """Cria o painel de alertas"""
    
    alerts_data = generate_alerts_data()
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4("🚨 Alertas de Performance", className="mb-0"),
                    dbc.Badge(len(alerts_data), color="danger", className="ms-2")
                ], className="d-flex align-items-center")
            ]),
            dbc.CardBody([
                html.Div([
                    create_alert_item(alert) for alert in alerts_data
                ], id="alerts-container", className="alerts-container")
            ])
        ])
    ])

def register_alerts_callbacks(app):
    """Registra callbacks para o painel de alertas"""
    
    @app.callback(
        Output("alerts-container", "children"),
        [Input("region-filter", "value"),
         Input("interval-component", "n_intervals")]
    )
    def update_alerts(region, n_intervals):
        """Atualiza os alertas baseado nos filtros"""
        
        alerts_data = generate_alerts_data()
        
        # Filtra alertas por região se necessário
        if region and region != "all":
            alerts_data = [alert for alert in alerts_data if region.lower() in alert['store'].lower()]
        
        return [create_alert_item(alert) for alert in alerts_data]
