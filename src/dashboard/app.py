# src/dashboard/app.py
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import sys

# Configurar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

print(f"🚀 Credit Control Dashboard com Análise Dinâmica")

# [MANTENHA TODO O CÓDIGO DE IMPORTAÇÃO E GERAÇÃO DE DADOS ANTERIOR...]

# Funções de análise dinâmica
def generate_segment_insights(data):
    """Gera insights automáticos para distribuição por segmento"""
    segment_stats = data.groupby('segmento').agg({
        'valor_contrato': ['count', 'sum', 'mean'],
        'dias_atraso': 'mean',
        'satisfacao_cliente': 'mean'
    }).round(2)
    
    segment_stats.columns = ['clientes', 'valor_total', 'valor_medio', 'atraso_medio', 'satisfacao_media']
    segment_stats = segment_stats.reset_index()
    
    total_clientes = len(data)
    insights = []
    
    for _, seg in segment_stats.iterrows():
        percentual = (seg['clientes'] / total_clientes) * 100
        insight = f"• {seg['segmento']}: {seg['clientes']} clientes ({percentual:.1f}%) - Valor médio: ${seg['valor_medio']:,.0f}"
        insights.append(insight)
    
    main_insight = f"💡 **Distribuição Balanceada**: {len(segment_stats)} segmentos com representatividade diversificada no portfolio."
    
    return main_insight, insights

def generate_risk_insights(data):
    """Gera insights automáticos para análise de risco"""
    risk_stats = data.groupby('risco_credito').agg({
        'cliente_id': 'count',
        'valor_contrato': 'sum',
        'dias_atraso': 'mean',
        'valor_em_risco': 'sum'
    }).round(2)
    
    risk_stats = risk_stats.reset_index()
    total_risk_exposure = risk_stats['valor_em_risco'].sum()
    
    insights = []
    for _, risk in risk_stats.iterrows():
        risk_percent = (risk['valor_em_risco'] / total_risk_exposure) * 100
        insight = f"• Risco {int(risk['risco_credito'])}: {risk['cliente_id']} clientes - ${risk['valor_em_risco']:,.0f} em risco ({risk_percent:.1f}%)"
        insights.append(insight)
    
    high_risk_count = len(data[data['risco_credito'] >= 4])
    high_risk_percent = (high_risk_count / len(data)) * 100
    
    main_insight = f"⚠️ **Alerta**: {high_risk_count} clientes ({high_risk_percent:.1f}%) classificados como alto risco necessitam atenção imediata."
    
    return main_insight, insights

def generate_satisfaction_insights(data):
    """Gera insights automáticos para análise de satisfação"""
    satisfaction_stats = data.groupby('segmento')['satisfacao_cliente'].agg(['mean', 'count']).round(2)
    satisfaction_stats = satisfaction_stats.reset_index()
    
    overall_satisfaction = data['satisfacao_cliente'].mean()
    low_satisfaction = data[data['satisfacao_cliente'] < 3]
    
    insights = []
    for _, seg in satisfaction_stats.iterrows():
        insight = f"• {seg['segmento']}: {seg['mean']}/5 de satisfação média"
        insights.append(insight)
    
    if len(low_satisfaction) > 0:
        low_sat_insight = f"🎯 **Oportunidade**: {len(low_satisfaction)} clientes com baixa satisfação (<3.0) identificados para ações de retenção."
    else:
        low_sat_insight = "✅ **Excelente**: Todos os clientes apresentam satisfação acima de 3.0."
    
    main_insight = f"😊 **Satisfação Geral**: {overall_satisfaction:.1f}/5 - {low_sat_insight}"
    
    return main_insight, insights

def generate_contract_insights(data):
    """Gera insights automáticos para análise de contratos"""
    contract_corr = data[['score_credito', 'valor_contrato', 'dias_atraso']].corr().iloc[0,1]
    
    high_value_clients = data[data['valor_contrato'] > data['valor_contrato'].quantile(0.8)]
    low_risk_high_value = high_value_clients[high_value_clients['risco_credito'] <= 2]
    
    insights = [
        f"• Correlação Score-Contrato: {contract_corr:.2f} (relação moderada)",
        f"• Clientes de Alto Valor: {len(high_value_clients)} clientes representam top 20% em valor",
        f"• Clientes Premium: {len(low_risk_high_value)} clientes com alto valor e baixo risco"
    ]
    
    main_insight = "💰 **Estratégia**: Focar em clientes de alto valor com baixo risco para maximizar retorno."
    
    return main_insight, insights

# [MANTENHA O CÓDIGO DE GERAÇÃO DE DADOS E KPIs...]

# Layout do dashboard com análises dinâmicas
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("💳 Credit Control Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': '5px'}),
        html.P(f"Branch: {BRANCH_NAME} | Análises Dinâmicas em Tempo Real",
               style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '14px', 'marginBottom': '20px'})
    ]),
    
    # KPIs
    html.Div([
        html.Div([
            html.H4("👥 Total Clientes", style={'color': '#2E86AB', 'marginBottom': '5px'}),
            html.H2(f"{kpis['total_clientes']:,}", 
                   style={'color': '#2E86AB', 'margin': '0', 'fontSize': '2em'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("⚠️ Inadimplência", style={'color': '#dc3545', 'marginBottom': '5px'}),
            html.H2(f"{kpis['taxa_inadimplencia']:.1f}%", 
                   style={'color': '#dc3545', 'margin': '0', 'fontSize': '2em'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("😊 Satisfação", style={'color': '#28a745', 'marginBottom': '5px'}),
            html.H2(f"{kpis['satisfacao_media']:.1f}/5", 
                   style={'color': '#28a745', 'margin': '0', 'fontSize': '2em'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("💰 Exposição", style={'color': '#ffc107', 'marginBottom': '5px'}),
            html.H2(f"${kpis['exposicao_total_credito']:,.0f}", 
                   style={'color': '#ffc107', 'margin': '0', 'fontSize': '1.8em'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '5px', 'flex': '1'}),
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'margin': '10px 0'}),
    
    # Gráfico 1: Distribuição por Segmento com Análise
    html.Div([
        html.Div([
            dcc.Graph(
                id='segment-distribution',
                figure=px.pie(
                    portfolio_data, 
                    names='segmento',
                    title='📊 Distribuição por Segmento de Cliente',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
            ),
            html.Div([
                html.H4("🎯 Análise do Segmento", style={'color': '#2E86AB', 'marginBottom': '10px'}),
                html.P(id='segment-main-insight', style={'fontWeight': 'bold', 'color': '#2E86AB'}),
                html.Div(id='segment-details', style={'marginTop': '10px'})
            ], style={'padding': '15px', 'backgroundColor': '#f0f8ff', 'borderRadius': '8px', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px', 'verticalAlign': 'top'}),
        
        # Gráfico 2: Análise de Risco com Insights
        html.Div([
            dcc.Graph(
                id='risk-distribution',
                figure=px.bar(
                    portfolio_data.groupby('risco_credito').size().reset_index(name='count'),
                    x='risco_credito',
                    y='count',
                    title='🎯 Clientes por Nível de Risco',
                    color='risco_credito',
                    color_discrete_sequence=['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1', '#000000']
                )
            ),
            html.Div([
                html.H4("⚠️ Análise de Risco", style={'color': '#dc3545', 'marginBottom': '10px'}),
                html.P(id='risk-main-insight', style={'fontWeight': 'bold', 'color': '#dc3545'}),
                html.Div(id='risk-details', style={'marginTop': '10px'})
            ], style={'padding': '15px', 'backgroundColor': '#fff0f0', 'borderRadius': '8px', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px', 'verticalAlign': 'top'})
    ]),
    
    # Gráfico 3: Satisfação com Análise
    html.Div([
        html.Div([
            dcc.Graph(
                id='satisfaction-analysis',
                figure=px.box(
                    portfolio_data,
                    x='segmento',
                    y='satisfacao_cliente',
                    title='😊 Satisfação do Cliente por Segmento',
                    color='segmento'
                )
            ),
            html.Div([
                html.H4("📈 Análise de Satisfação", style={'color': '#28a745', 'marginBottom': '10px'}),
                html.P(id='satisfaction-main-insight', style={'fontWeight': 'bold', 'color': '#28a745'}),
                html.Div(id='satisfaction-details', style={'marginTop': '10px'})
            ], style={'padding': '15px', 'backgroundColor': '#f0fff0', 'borderRadius': '8px', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px', 'verticalAlign': 'top'}),
        
        # Gráfico 4: Contratos com Análise
        html.Div([
            dcc.Graph(
                id='contract-analysis',
                figure=px.scatter(
                    portfolio_data,
                    x='score_credito',
                    y='valor_contrato',
                    color='risco_credito',
                    title='💰 Score vs Valor do Contrato',
                    size='valor_contrato',
                    hover_data=['segmento', 'dias_atraso'],
                    color_discrete_map={'Baixo': '#28a745', 'Médio': '#ffc107', 'Alto': '#dc3545'}
                )
            ),
            html.Div([
                html.H4("💼 Análise de Contratos", style={'color': '#ffc107', 'marginBottom': '10px'}),
                html.P(id='contract-main-insight', style={'fontWeight': 'bold', 'color': '#ffc107'}),
                html.Div(id='contract-details', style={'marginTop': '10px'})
            ], style={'padding': '15px', 'backgroundColor': '#fffbf0', 'borderRadius': '8px', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px', 'verticalAlign': 'top'})
    ]),
    
    # Resumo Executivo
    html.Div([
        html.H3("📋 Resumo Executivo & Recomendações", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'margin': '20px 0'}),
        html.Div([
            html.H4("🎯 Recomendações Estratégicas", style={'color': '#2E86AB'}),
            html.Ul([
                html.Li("Focar em clientes Corporate que representam maior valor médio por contrato"),
                html.Li("Implementar programa de recuperação para clientes com risco 4+"),
                html.Li("Desenvolver campanhas de fidelização para segmentos com satisfação média"),
                html.Li("Otimizar limites de crédito baseado no score e histórico de pagamento")
            ], style={'lineHeight': '1.6'})
        ], style={'padding': '20px', 'backgroundColor': '#e8f4f8', 'borderRadius': '8px'})
    ], style={'margin': '20px'}),
    
    # Tabela de Dados
    html.Div([
        html.H3("📋 Detalhes do Portfolio", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'margin': '20px 0'}),
        dash_table.DataTable(
            data=portfolio_data.head(10).to_dict('records'),
            columns=[{"name": i, "id": i} for i in ['cliente_id', 'segmento', 'valor_contrato', 'dias_atraso', 'risco_credito', 'satisfacao_cliente']],
            page_size=8,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px', 'fontFamily': 'Arial'},
            style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'}
        )
    ], style={'margin': '10px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P(f"✅ Credit Control Dashboard com Análise Dinâmica | Branch: {BRANCH_NAME} | " 
               "💼 Demonstração para vaga Junior Data & Reporting Officer",
              style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '0.8em', 'marginTop': '20px'})
    ])
])

# Callbacks para análises dinâmicas
@app.callback(
    [Output('segment-main-insight', 'children'),
     Output('segment-details', 'children')],
    [Input('segment-distribution', 'figure')]
)
def update_segment_insights(figure):
    main_insight, details = generate_segment_insights(portfolio_data)
    details_html = [html.P(detail) for detail in details]
    return main_insight, details_html

@app.callback(
    [Output('risk-main-insight', 'children'),
     Output('risk-details', 'children')],
    [Input('risk-distribution', 'figure')]
)
def update_risk_insights(figure):
    main_insight, details = generate_risk_insights(portfolio_data)
    details_html = [html.P(detail) for detail in details]
    return main_insight, details_html

@app.callback(
    [Output('satisfaction-main-insight', 'children'),
     Output('satisfaction-details', 'children')],
    [Input('satisfaction-analysis', 'figure')]
)
def update_satisfaction_insights(figure):
    main_insight, details = generate_satisfaction_insights(portfolio_data)
    details_html = [html.P(detail) for detail in details]
    return main_insight, details_html

@app.callback(
    [Output('contract-main-insight', 'children'),
     Output('contract-details', 'children')],
    [Input('contract-analysis', 'figure')]
)
def update_contract_insights(figure):
    main_insight, details = generate_contract_insights(portfolio_data)
    details_html = [html.P(detail) for detail in details]
    return main_insight, details_html

# Server configuration
server = app.server

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    debug = False if os.environ.get('RENDER') else True
    
    print(f"🌈 Dashboard com Análise Dinâmica rodando em: http://0.0.0.0:{port}")
    app.run_server(host='0.0.0.0', port=port, debug=debug)