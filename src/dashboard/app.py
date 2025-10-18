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

print(f"🚀 Credit Control Dashboard com Filtros Interativos")

# Definir variáveis de ambiente
BRANCH_NAME = os.environ.get('GIT_BRANCH', 'pipeline-car-dev')
REPOSITORY = os.environ.get('REPOSITORY', 'cabicho/portfolio_projectos')

# Tentar importar os módulos com fallback
try:
    from data_sources.financial_data import CreditControlData
    print("✅ Módulo financial_data importado com sucesso!")
    
    # Fallback para CustomerAnalytics
    class CustomerAnalytics:
        def __init__(self, data):
            self.data = data
        
        def calculate_kpis(self, filtered_data=None):
            data_to_use = filtered_data if filtered_data is not None else self.data
            total_clientes = len(data_to_use)
            clientes_ativos = len(data_to_use[data_to_use.get('estado_conta', 'Ativo') == 'Ativo'])
            clientes_inadimplentes = len(data_to_use[data_to_use['dias_atraso'] > 90])
            
            return {
                'total_clientes': total_clientes,
                'clientes_ativos': clientes_ativos,
                'taxa_inadimplencia': (clientes_inadimplentes / total_clientes) * 100 if total_clientes > 0 else 0,
                'satisfacao_media': data_to_use['satisfacao_cliente'].mean() if total_clientes > 0 else 0,
                'utilizacao_media_credito': data_to_use.get('utilizacao_credito', 0.5).mean() * 100 if total_clientes > 0 else 0,
                'exposicao_total_credito': data_to_use['valor_contrato'].sum(),
                'valor_total_risco': data_to_use.get('valor_em_risco', 0).sum(),
                'score_medio_credito': data_to_use['score_credito'].mean() if total_clientes > 0 else 0
            }
        
        def segment_clients(self, data):
            segments = []
            for _, client in data.iterrows():
                risco = client.get('risco_credito', 0)
                valor_contrato = client['valor_contrato']
                
                if risco <= 2 and valor_contrato > 10000:
                    segment = 'Premium'
                elif risco >= 4:
                    segment = 'Alto Risco'
                elif client.get('utilizacao_credito', 0) > 0.8:
                    segment = 'Alta Utilização'
                elif client['dias_atraso'] > 30:
                    segment = 'Atraso Crítico'
                else:
                    segment = 'Standard'
                segments.append(segment)
            return segments
                
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    print("🔄 Usando fallback completo...")
    
    # Fallback completo
    class CreditControlData:
        def __init__(self, sample_size=1000):
            self.sample_size = sample_size
            np.random.seed(42)
        
        def generate_portfolio_data(self):
            data = {
                'cliente_id': range(1, self.sample_size + 1),
                'segmento': np.random.choice(['Corporate', 'SME', 'Individual'], self.sample_size),
                'valor_contrato': np.random.uniform(1000, 50000, self.sample_size),
                'dias_atraso': np.random.randint(0, 120, self.sample_size),
                'limite_credito': np.random.uniform(5000, 100000, self.sample_size),
                'utilizacao_credito': np.random.uniform(0.1, 0.95, self.sample_size),
                'score_credito': np.random.randint(300, 850, self.sample_size),
                'estado_conta': np.random.choice(['Ativo', 'Inativo', 'Suspenso'], self.sample_size),
                'satisfacao_cliente': np.random.uniform(1, 5, self.sample_size),
                'tempo_cliente_meses': np.random.randint(1, 60, self.sample_size),
                'regiao': np.random.choice(['Norte', 'Sul', 'Centro', 'Litoral'], self.sample_size)
            }
            
            df = pd.DataFrame(data)
            df['risco_credito'] = df.apply(self.calculate_credit_risk, axis=1)
            df['categoria_atraso'] = df['dias_atraso'].apply(self.categorize_delay)
            df['valor_em_risco'] = df.apply(self.calculate_risk_exposure, axis=1)
            return df
        
        def calculate_credit_risk(self, row):
            risk_score = 0
            if row['dias_atraso'] > 90:
                risk_score += 3
            elif row['dias_atraso'] > 30:
                risk_score += 2
            elif row['dias_atraso'] > 0:
                risk_score += 1
                
            if row['utilizacao_credito'] > 0.8:
                risk_score += 2
            elif row['utilizacao_credito'] > 0.5:
                risk_score += 1
                
            if row['score_credito'] < 500:
                risk_score += 3
            elif row['score_credito'] < 650:
                risk_score += 2
                
            return min(risk_score, 5)
        
        def categorize_delay(self, dias):
            if dias == 0:
                return 'Em dia'
            elif dias <= 30:
                return 'Atraso leve'
            elif dias <= 90:
                return 'Atraso moderado'
            else:
                return 'Atraso severo'
        
        def calculate_risk_exposure(self, row):
            risk_multiplier = {0: 0.01, 1: 0.05, 2: 0.10, 3: 0.25, 4: 0.50, 5: 0.75}
            return row['valor_contrato'] * risk_multiplier.get(row['risco_credito'], 0.1)
    
    class CustomerAnalytics:
        def __init__(self, data):
            self.data = data
        
        def calculate_kpis(self, filtered_data=None):
            data_to_use = filtered_data if filtered_data is not None else self.data
            total_clientes = len(data_to_use)
            clientes_ativos = len(data_to_use[data_to_use['estado_conta'] == 'Ativo'])
            clientes_inadimplentes = len(data_to_use[data_to_use['dias_atraso'] > 90])
            
            return {
                'total_clientes': total_clientes,
                'clientes_ativos': clientes_ativos,
                'taxa_inadimplencia': (clientes_inadimplentes / total_clientes) * 100 if total_clientes > 0 else 0,
                'satisfacao_media': data_to_use['satisfacao_cliente'].mean() if total_clientes > 0 else 0,
                'utilizacao_media_credito': data_to_use['utilizacao_credito'].mean() * 100 if total_clientes > 0 else 0,
                'exposicao_total_credito': data_to_use['valor_contrato'].sum(),
                'valor_total_risco': data_to_use['valor_em_risco'].sum(),
                'score_medio_credito': data_to_use['score_credito'].mean() if total_clientes > 0 else 0
            }
        
        def segment_clients(self, data):
            return ['Standard'] * len(data)

# Funções de análise dinâmica - ATUALIZADAS para usar dados filtrados corretamente
def generate_segment_insights(filtered_data):
    """Gera insights automáticos para distribuição por segmento"""
    if len(filtered_data) == 0:
        return "📊 Nenhum dado para análise", []
    
    segment_stats = filtered_data.groupby('segmento').agg({
        'valor_contrato': ['count', 'sum', 'mean'],
        'dias_atraso': 'mean',
        'satisfacao_cliente': 'mean'
    }).round(2)
    
    segment_stats.columns = ['clientes', 'valor_total', 'valor_medio', 'atraso_medio', 'satisfacao_media']
    segment_stats = segment_stats.reset_index()
    
    total_clientes = len(filtered_data)
    insights = []
    
    for _, seg in segment_stats.iterrows():
        percentual = (seg['clientes'] / total_clientes) * 100
        insight = f"• {seg['segmento']}: {seg['clientes']} clientes ({percentual:.1f}%) - Valor médio: ${seg['valor_medio']:,.0f}"
        insights.append(insight)
    
    main_insight = f"💡 **Distribuição**: {len(segment_stats)} segmentos analisados"
    
    return main_insight, insights

def generate_risk_insights(filtered_data):
    """Gera insights automáticos para análise de risco"""
    if len(filtered_data) == 0:
        return "⚠️ Nenhum dado para análise", []
    
    risk_stats = filtered_data.groupby('risco_credito').agg({
        'cliente_id': 'count',
        'valor_contrato': 'sum',
        'dias_atraso': 'mean',
        'valor_em_risco': 'sum'
    }).round(2)
    
    risk_stats = risk_stats.reset_index()
    total_risk_exposure = risk_stats['valor_em_risco'].sum()
    
    insights = []
    for _, risk in risk_stats.iterrows():
        risk_percent = (risk['valor_em_risco'] / total_risk_exposure) * 100 if total_risk_exposure > 0 else 0
        insight = f"• Risco {int(risk['risco_credito'])}: {risk['cliente_id']} clientes - ${risk['valor_em_risco']:,.0f} em risco ({risk_percent:.1f}%)"
        insights.append(insight)
    
    high_risk_count = len(filtered_data[filtered_data['risco_credito'] >= 4])
    high_risk_percent = (high_risk_count / len(filtered_data)) * 100 if len(filtered_data) > 0 else 0
    
    main_insight = f"⚠️ **Alerta**: {high_risk_count} clientes ({high_risk_percent:.1f}%) classificados como alto risco"
    
    return main_insight, insights

def generate_satisfaction_insights(filtered_data):
    """Gera insights automáticos para análise de satisfação"""
    if len(filtered_data) == 0:
        return "😊 Nenhum dado para análise", []
    
    satisfaction_stats = filtered_data.groupby('segmento')['satisfacao_cliente'].agg(['mean', 'count']).round(2)
    satisfaction_stats = satisfaction_stats.reset_index()
    
    overall_satisfaction = filtered_data['satisfacao_cliente'].mean()
    low_satisfaction = filtered_data[filtered_data['satisfacao_cliente'] < 3]
    
    insights = []
    for _, seg in satisfaction_stats.iterrows():
        insight = f"• {seg['segmento']}: {seg['mean']}/5 de satisfação média"
        insights.append(insight)
    
    if len(low_satisfaction) > 0:
        low_sat_insight = f"🎯 **Oportunidade**: {len(low_satisfaction)} clientes com baixa satisfação (<3.0)"
    else:
        low_sat_insight = "✅ **Excelente**: Todos os clientes com satisfação acima de 3.0"
    
    main_insight = f"😊 **Satisfação Geral**: {overall_satisfaction:.1f}/5 - {low_sat_insight}"
    
    return main_insight, insights

def generate_contract_insights(filtered_data):
    """Gera insights automáticos para análise de contratos"""
    if len(filtered_data) == 0:
        return "💰 Nenhum dado para análise", []
    
    contract_corr = filtered_data[['score_credito', 'valor_contrato', 'dias_atraso']].corr().iloc[0,1]
    
    high_value_clients = filtered_data[filtered_data['valor_contrato'] > filtered_data['valor_contrato'].quantile(0.8)] if len(filtered_data) > 0 else filtered_data
    low_risk_high_value = high_value_clients[high_value_clients['risco_credito'] <= 2]
    
    insights = [
        f"• Correlação Score-Contrato: {contract_corr:.2f}",
        f"• Clientes de Alto Valor: {len(high_value_clients)} clientes (top 20%)",
        f"• Clientes Premium: {len(low_risk_high_value)} clientes com alto valor e baixo risco"
    ]
    
    main_insight = "💰 **Estratégia**: Focar em clientes de alto valor com baixo risco"
    
    return main_insight, insights

# Função auxiliar para aplicar filtros - ATUALIZADA
def apply_filters(data, segmento, valor_contrato, dias_atraso, risco, satisfacao):
    filtered_data = data.copy()
    
    if segmento != 'all':
        filtered_data = filtered_data[filtered_data['segmento'] == segmento]
    
    if valor_contrato is not None and valor_contrato != '':
        filtered_data = filtered_data[filtered_data['valor_contrato'] >= float(valor_contrato)]
    
    if dias_atraso is not None and dias_atraso != '':
        filtered_data = filtered_data[filtered_data['dias_atraso'] >= int(dias_atraso)]
    
    if risco is not None and risco > 0:
        filtered_data = filtered_data[filtered_data['risco_credito'] >= risco]
    
    if satisfacao is not None and satisfacao != '':
        filtered_data = filtered_data[filtered_data['satisfacao_cliente'] >= float(satisfacao)]
    
    return filtered_data

# Gerar dados iniciais
print("📊 Gerando dados do portfolio...")
data_generator = CreditControlData(sample_size=800)
portfolio_data_full = data_generator.generate_portfolio_data()
analytics = CustomerAnalytics(portfolio_data_full)

# Inicializar app
app = dash.Dash(__name__)
app.title = "Credit Control Analytics"

# Layout do dashboard com filtros
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("💳 Credit Control Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': '5px'}),
        html.P(f"Branch: {BRANCH_NAME} | Filtros Interativos & Análise Dinâmica",
               style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '14px', 'marginBottom': '20px'})
    ]),
    
    # Filtros Interativos
    html.Div([
        html.Div([
            html.Label("🏢 Segmento:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='segmento-filter',
                options=[{'label': 'Todos', 'value': 'all'}] + 
                        [{'label': seg, 'value': seg} for seg in sorted(portfolio_data_full['segmento'].unique())],
                value='all',
                style={'width': '200px', 'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'marginRight': '20px', 'marginBottom': '10px'}),
        
        html.Div([
            html.Label("💰 Valor Contrato (>):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(
                id='valor-contrato-filter',
                type='number',
                placeholder='Ex: 10000',
                style={'width': '120px', 'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'marginRight': '20px', 'marginBottom': '10px'}),
        
        html.Div([
            html.Label("📅 Dias Atraso (>):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(
                id='dias-atraso-filter',
                type='number',
                placeholder='Ex: 30',
                min=0,
                max=120,
                style={'width': '100px', 'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'marginRight': '20px', 'marginBottom': '10px'}),
    ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '10px'}),
    
    html.Div([
        html.Div([
            html.Label("⚠️ Risco Crédito (≥):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='risco-filter',
                options=[{'label': 'Todos', 'value': 0}] + 
                        [{'label': f'Risco ≥ {i}', 'value': i} for i in range(1, 6)],
                value=0,
                style={'width': '150px', 'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'marginRight': '20px', 'marginBottom': '10px'}),
        
        html.Div([
            html.Label("😊 Satisfação (≥):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(
                id='satisfacao-filter',
                type='number',
                placeholder='Ex: 3.0',
                min=1,
                max=5,
                step=0.5,
                style={'width': '100px', 'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'marginRight': '20px', 'marginBottom': '10px'}),
        
        html.Div([
            html.Button("🔄 Limpar Filtros", id='clear-filters', n_clicks=0,
                       style={'backgroundColor': '#6c757d', 'color': 'white', 'border': 'none', 'padding': '8px 15px', 'borderRadius': '5px'})
        ], style={'display': 'inline-block', 'marginBottom': '10px'})
    ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '10px'}),
    
    # KPIs Dinâmicos
    html.Div(id='kpis-container', style={'margin': '20px 0'}),
    
    # Gráficos com Análises
    html.Div([
        html.Div([
            dcc.Graph(id='segment-distribution'),
            html.Div([
                html.H4("🎯 Análise do Segmento", style={'color': '#2E86AB', 'marginBottom': '10px'}),
                html.P(id='segment-main-insight', style={'fontWeight': 'bold', 'color': '#2E86AB'}),
                html.Div(id='segment-details', style={'marginTop': '10px'})
            ], style={'padding': '15px', 'backgroundColor': '#f0f8ff', 'borderRadius': '8px', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='risk-distribution'),
            html.Div([
                html.H4("⚠️ Análise de Risco", style={'color': '#dc3545', 'marginBottom': '10px'}),
                html.P(id='risk-main-insight', style={'fontWeight': 'bold', 'color': '#dc3545'}),
                html.Div(id='risk-details', style={'marginTop': '10px'})
            ], style={'padding': '15px', 'backgroundColor': '#fff0f0', 'borderRadius': '8px', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px', 'verticalAlign': 'top'})
    ]),
    
    html.Div([
        html.Div([
            dcc.Graph(id='satisfaction-analysis'),
            html.Div([
                html.H4("📈 Análise de Satisfação", style={'color': '#28a745', 'marginBottom': '10px'}),
                html.P(id='satisfaction-main-insight', style={'fontWeight': 'bold', 'color': '#28a745'}),
                html.Div(id='satisfaction-details', style={'marginTop': '10px'})
            ], style={'padding': '15px', 'backgroundColor': '#f0fff0', 'borderRadius': '8px', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='contract-analysis'),
            html.Div([
                html.H4("💼 Análise de Contratos", style={'color': '#ffc107', 'marginBottom': '10px'}),
                html.P(id='contract-main-insight', style={'fontWeight': 'bold', 'color': '#ffc107'}),
                html.Div(id='contract-details', style={'marginTop': '10px'})
            ], style={'padding': '15px', 'backgroundColor': '#fffbf0', 'borderRadius': '8px', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px', 'verticalAlign': 'top'})
    ]),
    
    # Tabela de Dados Filtrada
    html.Div([
        html.H3("📋 Detalhes do Portfolio (Filtrado)", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'margin': '20px 0'}),
        html.Div(id='data-table-container')
    ], style={'margin': '10px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P(f"✅ Credit Control Dashboard com Filtros Interativos | Branch: {BRANCH_NAME} | " 
               "💼 Demonstração para vaga Junior Data & Reporting Officer",
              style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '0.8em', 'marginTop': '20px'})
    ])
])

# Callback principal para filtros - ATUALIZADO para sincronizar tudo
@app.callback(
    [Output('kpis-container', 'children'),
     Output('segment-distribution', 'figure'),
     Output('risk-distribution', 'figure'),
     Output('satisfaction-analysis', 'figure'),
     Output('contract-analysis', 'figure'),
     Output('data-table-container', 'children'),
     Output('segment-main-insight', 'children'),
     Output('segment-details', 'children'),
     Output('risk-main-insight', 'children'),
     Output('risk-details', 'children'),
     Output('satisfaction-main-insight', 'children'),
     Output('satisfaction-details', 'children'),
     Output('contract-main-insight', 'children'),
     Output('contract-details', 'children'),
     Output('segmento-filter', 'value'),
     Output('valor-contrato-filter', 'value'),
     Output('dias-atraso-filter', 'value'),
     Output('risco-filter', 'value'),
     Output('satisfacao-filter', 'value')],
    [Input('segmento-filter', 'value'),
     Input('valor-contrato-filter', 'value'),
     Input('dias-atraso-filter', 'value'),
     Input('risco-filter', 'value'),
     Input('satisfacao-filter', 'value'),
     Input('clear-filters', 'n_clicks')]
)
def update_dashboard(segmento, valor_contrato, dias_atraso, risco, satisfacao, clear_clicks):
    # Aplicar filtros
    filtered_data = apply_filters(portfolio_data_full, segmento, valor_contrato, dias_atraso, risco, satisfacao)
    
    # Limpar filtros se botão foi clicado
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'clear-filters.n_clicks':
        filtered_data = portfolio_data_full
        segmento = 'all'
        valor_contrato = None
        dias_atraso = None
        risco = 0
        satisfacao = None
    
    # Calcular KPIs com dados filtrados
    kpis = analytics.calculate_kpis(filtered_data)
    segments = analytics.segment_clients(filtered_data)
    filtered_data_with_segments = filtered_data.copy()
    filtered_data_with_segments['segmento_cliente'] = segments
    
    # KPIs atualizados
    kpis_container = html.Div([
        html.Div([
            html.H4("👥 Clientes Filtrados", style={'color': '#2E86AB', 'marginBottom': '5px'}),
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
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'margin': '10px 0'})
    
    # Gráficos atualizados
    segment_fig = px.pie(
        filtered_data, 
        names='segmento',
        title='📊 Distribuição por Segmento',
        color_discrete_sequence=px.colors.qualitative.Set3
    ) if len(filtered_data) > 0 else go.Figure()
    
    risk_fig = px.bar(
        filtered_data.groupby('risco_credito').size().reset_index(name='count'),
        x='risco_credito',
        y='count',
        title='🎯 Clientes por Nível de Risco',
        color='risco_credito',
        color_discrete_sequence=['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1', '#000000']
    ) if len(filtered_data) > 0 else go.Figure()
    
    satisfaction_fig = px.box(
        filtered_data,
        x='segmento',
        y='satisfacao_cliente',
        title='😊 Satisfação do Cliente por Segmento',
        color='segmento'
    ) if len(filtered_data) > 0 else go.Figure()
    
    contract_fig = px.scatter(
        filtered_data,
        x='score_credito',
        y='valor_contrato',
        color='risco_credito',
        title='💰 Score vs Valor do Contrato',
        size='valor_contrato',
        hover_data=['segmento', 'dias_atraso'],
        color_discrete_map={0: '#28a745', 1: '#ffc107', 2: '#fd7e14', 3: '#dc3545', 4: '#6f42c1', 5: '#000000'}
    ) if len(filtered_data) > 0 else go.Figure()
    
    # Tabela atualizada
    table = dash_table.DataTable(
        data=filtered_data_with_segments.head(10).to_dict('records'),
        columns=[{"name": i, "id": i} for i in ['cliente_id', 'segmento', 'valor_contrato', 'dias_atraso', 'risco_credito', 'satisfacao_cliente', 'segmento_cliente']],
        page_size=8,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '8px', 'fontFamily': 'Arial'},
        style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'}
    ) if len(filtered_data) > 0 else html.P("Nenhum dado encontrado com os filtros aplicados.")
    
    # Análises dinâmicas atualizadas
    segment_main, segment_details_list = generate_segment_insights(filtered_data)
    segment_details = [html.P(detail) for detail in segment_details_list]
    
    risk_main, risk_details_list = generate_risk_insights(filtered_data)
    risk_details = [html.P(detail) for detail in risk_details_list]
    
    satisfaction_main, satisfaction_details_list = generate_satisfaction_insights(filtered_data)
    satisfaction_details = [html.P(detail) for detail in satisfaction_details_list]
    
    contract_main, contract_details_list = generate_contract_insights(filtered_data)
    contract_details = [html.P(detail) for detail in contract_details_list]
    
    return (kpis_container, segment_fig, risk_fig, satisfaction_fig, contract_fig, 
            table, segment_main, segment_details, risk_main, risk_details, 
            satisfaction_main, satisfaction_details, contract_main, contract_details,
            segmento, valor_contrato, dias_atraso, risco, satisfacao)

# Server configuration
server = app.server

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    debug = False if os.environ.get('RENDER') else True
    
    print(f"🌈 Dashboard com Filtros Interativos rodando em: http://0.0.0.0:{port}")
    app.run_server(host='0.0.0.0', port=port, debug=debug)