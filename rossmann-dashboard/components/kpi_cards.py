"""
Componente de KPI Cards para o Dashboard
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import pandas as pd
from data.mock_data import generate_mock_kpi_data

def create_kpi_card(kpi_id, title, value, change_percent, trend, detail, icon):
    """Cria um card individual de KPI"""
    
    trend_color = "success" if trend == "up" else "danger"
    trend_icon = "↗️" if trend == "up" else "↘️"
    change_display = f"+{change_percent}%" if trend == "up" else f"{change_percent}%"
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, className="kpi-icon"),
                html.H6(title, className="kpi-title")
            ], className="kpi-header"),
            
            html.H2(value, className="kpi-value", id=f"{kpi_id}-value"),
            
            html.Div([
                html.Span(trend_icon, className="trend-icon"),
                html.Span(change_display, className=f"text-{trend_color}"),
                html.Span(" vs período anterior", className="text-muted comparison-text")
            ], className="kpi-trend"),
            
            html.Small(detail, className="kpi-detail")
        ])
    ], className="kpi-card", id=kpi_id)

def create_kpi_cards_component():
    """Cria o layout completo dos KPI Cards"""
    
    kpi_data = generate_mock_kpi_data()
    
    return dbc.Row([
        dbc.Col(create_kpi_card(
            kpi_id="kpi-revenue",
            title="💰 Faturamento Total Previsto",
            value="R$ 285.9M",
            change_percent=kpi_data["total_revenue"]["change_percent"],
            trend=kpi_data["total_revenue"]["trend"],
            detail="Próximas 6 semanas",
            icon="💰"
        ), width=3, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            kpi_id="kpi-eligible",
            title="🏪 Lojas Elegíveis Reforma", 
            value="1,247",
            change_percent=kpi_data["eligible_stores"]["change_percent"],
            trend=kpi_data["eligible_stores"]["trend"],
            detail="63% da rede (1,978 lojas)",
            icon="✅"
        ), width=3, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            kpi_id="kpi-accuracy",
            title="🎯 Precisão do Modelo",
            value="89.2%",
            change_percent=kpi_data["model_accuracy"]["change_percent"],
            trend=kpi_data["model_accuracy"]["trend"],
            detail="MAPE (6 semanas)",
            icon="🎯"
        ), width=3, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            kpi_id="kpi-attention", 
            title="⚠️ Lojas em Atenção",
            value="84",
            change_percent=kpi_data["attention_stores"]["change_percent"],
            trend=kpi_data["attention_stores"]["trend"],
            detail="Performance crítica",
            icon="🔍"
        ), width=3, className="mb-3")
    ], className="kpi-row", id="kpi-cards-container")

def register_kpi_callbacks(app):
    """Registra os callbacks para atualização dos KPIs"""
    
    @app.callback(
        [Output("kpi-revenue-value", "children"),
         Output("kpi-eligible-value", "children"), 
         Output("kpi-accuracy-value", "children"),
         Output("kpi-attention-value", "children")],
        [Input("region-filter", "value"),
         Input("store-type-filter", "value"),
         Input("performance-filter", "value"),
         Input("interval-component", "n_intervals")]
    )
    def update_kpi_cards(region, store_type, performance, n_intervals):
        """Atualiza os valores dos KPIs baseado nos filtros"""
        
        updated_data = generate_mock_kpi_data()
        filtered_data = apply_filters_to_kpis(updated_data, region, store_type, performance)
        
        revenue_value = f"R$ {filtered_data['total_revenue']['current']/1000000:.1f}M"
        eligible_value = f"{filtered_data['eligible_stores']['current']:,}"
        accuracy_value = f"{filtered_data['model_accuracy']['current']}%"
        attention_value = f"{filtered_data['attention_stores']['current']}"
        
        return revenue_value, eligible_value, accuracy_value, attention_value

    def apply_filters_to_kpis(data, region, store_type, performance):
        """Aplica lógica de filtros aos dados dos KPIs"""
        filtered_data = data.copy()
        
        if region and region != "all":
            adjustment = 0.8
            filtered_data["total_revenue"]["current"] *= adjustment
            filtered_data["eligible_stores"]["current"] = int(filtered_data["eligible_stores"]["current"] * adjustment)
            
        if store_type and store_type != "all":
            adjustment = 0.9
            filtered_data["total_revenue"]["current"] *= adjustment
            filtered_data["eligible_stores"]["current"] = int(filtered_data["eligible_stores"]["current"] * adjustment)
            
        return filtered_data

def initialize_kpi_cards(app):
    """Função principal para inicializar o módulo de KPI Cards"""
    register_kpi_callbacks(app)
    return create_kpi_cards_component()
