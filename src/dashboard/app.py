import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging
import os
import sys

# ADICIONAR ESTA LINHA PARA CORRIGIR O PATH
sys.path.append('/app/src')

# Agora importar os módulos
from data_sources.financial_data import CreditControlData
from analysis.customer_analytics import CustomerAnalytics


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar app
app = dash.Dash(__name__)
app.title = "Credit Control Analytics"

# Gerar dados
logger.info("Inicializando gerador de dados...")
try:
    data_generator = CreditControlData(sample_size=1000)
    portfolio_data = data_generator.generate_portfolio_data()
    analytics = CustomerAnalytics(portfolio_data)
    kpis = analytics.calculate_kpis()
    segments = analytics.segment_clients()
    portfolio_data['segmento_cliente'] = segments
    logger.info("Dados gerados com sucesso!")
except Exception as e:
    logger.error(f"Erro ao gerar dados: {e}")
    # Criar dados de fallback
    portfolio_data = pd.DataFrame({
        'cliente_id': [1, 2, 3],
        'segmento': ['Corporate', 'SME', 'Individual'],
        'valor_contrato': [10000, 5000, 2000],
        'dias_atraso': [0, 15, 45],
        'risco_credito': [1, 2, 4],
        'satisfacao_cliente': [4.5, 3.8, 2.5],
        'segmento_cliente': ['Premium', 'Standard', 'Alto Risco']
    })
    kpis = {'total_clientes': 3, 'taxa_inadimplencia': 33.3, 'satisfacao_media': 3.6, 'exposicao_total_credito': 17000}
    


# Layout do dashboard
app.layout = html.Div([
    html.H1("📈 Credit Control & Customer Analytics Dashboard", 
            style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': 30}),
    
    # KPIs em Destaque
    html.Div([
        html.Div([
            html.H4("👥 Total Clientes", style={'color': '#2E86AB', 'marginBottom': '10px'}),
            html.H2(f"{kpis['total_clientes']:,}", 
                   style={'color': '#2E86AB', 'margin': '0', 'fontSize': '2.5em'})
        ], className='three columns', style={
            'textAlign': 'center', 
            'padding': '20px', 
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'margin': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }),
        
        html.Div([
            html.H4("⚠️ Taxa Inadimplência", style={'color': '#A23B72', 'marginBottom': '10px'}),
            html.H2(f"{kpis['taxa_inadimplencia']:.1f}%", 
                   style={'color': '#A23B72', 'margin': '0', 'fontSize': '2.5em'})
        ], className='three columns', style={
            'textAlign': 'center', 
            'padding': '20px', 
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'margin': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }),
        
        html.Div([
            html.H4("😊 Satisfação Cliente", style={'color': '#F18F01', 'marginBottom': '10px'}),
            html.H2(f"{kpis['satisfacao_media']:.1f}/5", 
                   style={'color': '#F18F01', 'margin': '0', 'fontSize': '2.5em'})
        ], className='three columns', style={
            'textAlign': 'center', 
            'padding': '20px', 
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'margin': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }),
        
        html.Div([
            html.H4("💰 Exposição Crédito", style={'color': '#C73E1D', 'marginBottom': '10px'}),
            html.H2(f"${kpis['exposicao_total_credito']:,.0f}", 
                   style={'color': '#C73E1D', 'margin': '0', 'fontSize': '2.5em'})
        ], className='three columns', style={
            'textAlign': 'center', 
            'padding': '20px', 
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'margin': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    ], className='row', style={'display': 'flex', 'justifyContent': 'center'}),
    
    # Filtros
    html.Div([
        html.Div([
            html.Label("Segmento de Cliente:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='segment-filter',
                options=[{'label': 'Todos', 'value': 'Todos'}] + 
                        [{'label': seg, 'value': seg} for seg in portfolio_data['segmento'].unique()],
                value='Todos',
                style={'width': '200px', 'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'marginRight': '20px'}),
        
        html.Div([
            html.Label("Nível de Risco:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='risk-filter',
                options=[{'label': 'Todos', 'value': 'Todos'}] + 
                        [{'label': f'Risco {i}', 'value': i} for i in range(6)],
                value='Todos',
                style={'width': '150px', 'display': 'inline-block'}
            )
        ], style={'display': 'inline-block'})
    ], style={'textAlign': 'center', 'margin': '30px 0'}),
    
    # Primeira linha de gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='risk-distribution')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='portfolio-composition')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ], style={'textAlign': 'center'}),
    
    # Segunda linha de gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='satisfaction-analysis')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='delay-analysis')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ], style={'textAlign': 'center'}),
    
    # Tabela de Dados
    html.Div([
        html.H3("📋 Detalhes do Portfolio de Clientes", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginTop': '40px'}),
        html.Div(id='client-table',
                style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})
    ]),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P("💼 Credit Control Dashboard - Desenvolvido para demonstração de habilidades em Data & Reporting",
              style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '0.9em'})
    ], style={'marginTop': '40px'})
])

# Callbacks para interatividade
@app.callback(
    [Output('risk-distribution', 'figure'),
     Output('portfolio-composition', 'figure'),
     Output('satisfaction-analysis', 'figure'),
     Output('delay-analysis', 'figure'),
     Output('client-table', 'children')],
    [Input('segment-filter', 'value'),
     Input('risk-filter', 'value')]
)
def update_dashboard(segment, risk_level):
    logger.info(f"Atualizando dashboard com filtros: segmento={segment}, risco={risk_level}")
    
    # Filtrar dados
    filtered_data = portfolio_data.copy()
    
    if segment != 'Todos':
        filtered_data = filtered_data[filtered_data['segmento'] == segment]
    
    if risk_level != 'Todos':
        filtered_data = filtered_data[filtered_data['risco_credito'] == risk_level]
    
    # Gráfico 1: Distribuição de Risco
    risk_counts = filtered_data['risco_credito'].value_counts().sort_index()
    risk_fig = go.Figure(data=[
        go.Bar(x=[f'Risco {i}' for i in risk_counts.index], 
               y=risk_counts.values,
               marker_color=['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1', '#000000'])
    ])
    risk_fig.update_layout(
        title='Distribuição de Risco de Crédito',
        xaxis_title='Nível de Risco',
        yaxis_title='Número de Clientes'
    )
    
    # Gráfico 2: Composição do Portfolio
    segment_counts = filtered_data['segmento_cliente'].value_counts()
    composition_fig = px.pie(
        values=segment_counts.values, 
        names=segment_counts.index,
        title='Composição do Portfolio por Segmento',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Gráfico 3: Análise de Satisfação
    satisfaction_fig = px.box(
        filtered_data, 
        x='segmento', 
        y='satisfacao_cliente',
        title='Satisfação do Cliente por Segmento',
        color='segmento'
    )
    
    # Gráfico 4: Análise de Atrasos
    delay_fig = px.histogram(
        filtered_data, 
        x='dias_atraso',
        title='Distribuição de Dias em Atraso',
        nbins=20,
        color_discrete_sequence=['#ff6b6b']
    )
    delay_fig.update_layout(
        xaxis_title='Dias em Atraso',
        yaxis_title='Número de Clientes'
    )
    
    # Tabela
    display_columns = ['cliente_id', 'segmento', 'valor_contrato', 'dias_atraso', 
                      'risco_credito', 'satisfacao_cliente', 'segmento_cliente']
    
    table_data = filtered_data[display_columns].head(15).round(2)
    table = dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{"name": i, "id": i} for i in display_columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Arial'
        },
        style_header={
            'backgroundColor': '#2E86AB',
            'color': 'white',
            'fontWeight': 'bold'
        }
    )
    
    logger.info("Dashboard atualizado com sucesso")
    return risk_fig, composition_fig, satisfaction_fig, delay_fig, table

if __name__ == '__main__':
    logger.info("Iniciando servidor Dash...")
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=True
    )
