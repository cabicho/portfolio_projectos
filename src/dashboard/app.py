# src/dashboard/app.py
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import sys
import logging

# CORREÇÃO CRÍTICA: Configurar o path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

print(f"🚀 Iniciando Credit Control Dashboard no Render")
print(f"📍 Current directory: {current_dir}")
print(f"📁 Source directory: {src_dir}")
print(f"🐍 Python path: {sys.path}")

# Tentar importar os módulos com fallback
try:
    from data_sources.financial_data import CreditControlData
    print("✅ Módulo financial_data importado com sucesso!")
    
    # Tentar importar analytics (opcional)
    try:
        from analysis.customer_analytics import CustomerAnalytics
        print("✅ Módulo customer_analytics importado com sucesso!")
    except ImportError:
        print("⚠️  Módulo customer_analytics não encontrado, usando fallback...")
        # Fallback para CustomerAnalytics
        class CustomerAnalytics:
            def __init__(self, data):
                self.data = data
            
            def calculate_kpis(self):
                total_clientes = len(self.data)
                clientes_ativos = len(self.data[self.data['estado_conta'] == 'Ativo'])
                clientes_inadimplentes = len(self.data[self.data['dias_atraso'] > 90])
                
                return {
                    'total_clientes': total_clientes,
                    'clientes_ativos': clientes_ativos,
                    'taxa_inadimplencia': (clientes_inadimplentes / total_clientes) * 100,
                    'satisfacao_media': self.data['satisfacao_cliente'].mean(),
                    'utilizacao_media_credito': self.data['utilizacao_credito'].mean() * 100,
                    'exposicao_total_credito': self.data['valor_contrato'].sum(),
                    'valor_total_risco': self.data['valor_em_risco'].sum() if 'valor_em_risco' in self.data.columns else 0,
                    'score_medio_credito': self.data['score_credito'].mean()
                }
            
            def segment_clients(self):
                segments = []
                for _, client in self.data.iterrows():
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
            
            def generate_retention_insights(self):
                return {
                    'correlacao_satisfacao_tempo': self.data[['satisfacao_cliente', 'tempo_cliente_meses']].corr().iloc[0,1] if 'tempo_cliente_meses' in self.data.columns else 0,
                    'satisfacao_por_segmento': self.data.groupby('segmento')['satisfacao_cliente'].mean().to_dict(),
                }
                
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    print("🔄 Usando fallback completo...")
    
    # Fallback completo se financial_data não for encontrado
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
        
        def calculate_kpis(self):
            total_clientes = len(self.data)
            clientes_ativos = len(self.data[self.data['estado_conta'] == 'Ativo'])
            clientes_inadimplentes = len(self.data[self.data['dias_atraso'] > 90])
            
            return {
                'total_clientes': total_clientes,
                'clientes_ativos': clientes_ativos,
                'taxa_inadimplencia': (clientes_inadimplentes / total_clientes) * 100,
                'satisfacao_media': self.data['satisfacao_cliente'].mean(),
                'utilizacao_media_credito': self.data['utilizacao_credito'].mean() * 100,
                'exposicao_total_credito': self.data['valor_contrato'].sum(),
                'valor_total_risco': self.data['valor_em_risco'].sum(),
                'score_medio_credito': self.data['score_credito'].mean()
            }
        
        def segment_clients(self):
            return ['Standard'] * len(self.data)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Identificação do branch
BRANCH_NAME = os.environ.get('GIT_BRANCH', 'pipeline-car-dev')
REPOSITORY = os.environ.get('REPOSITORY', 'cabicho/portfolio_projectos')

# Gerar dados
print("📊 Gerando dados do portfolio...")
data_generator = CreditControlData(sample_size=800)
portfolio_data = data_generator.generate_portfolio_data()
analytics = CustomerAnalytics(portfolio_data)
kpis = analytics.calculate_kpis()
segments = analytics.segment_clients()
portfolio_data['segmento_cliente'] = segments

print(f"✅ Dados gerados com sucesso: {len(portfolio_data)} clientes")
print(f"📈 KPIs: {kpis['total_clientes']} clientes, {kpis['taxa_inadimplencia']:.1f}% inadimplência")

# Inicializar app
app = dash.Dash(__name__)
app.title = "Credit Control Analytics"

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("💳 Credit Control Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': '5px'}),
        html.P(f"Branch: {BRANCH_NAME} | Repositório: {REPOSITORY}",
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
    
    # Gráficos
    html.Div([
        html.Div([
            dcc.Graph(
                figure=px.pie(
                    portfolio_data, 
                    names='segmento',
                    title='📊 Distribuição por Segmento',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px'}),
        
        html.Div([
            dcc.Graph(
                figure=px.bar(
                    portfolio_data.groupby('risco_credito').size().reset_index(name='count'),
                    x='risco_credito',
                    y='count',
                    title='🎯 Clientes por Nível de Risco',
                    color='risco_credito',
                    color_discrete_sequence=px.colors.sequential.Reds
                )
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px'})
    ]),
    
    html.Div([
        html.Div([
            dcc.Graph(
                figure=px.box(
                    portfolio_data,
                    x='segmento',
                    y='valor_contrato',
                    title='💵 Valor do Contrato por Segmento',
                    color='segmento'
                )
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px'}),
        
        html.Div([
            dcc.Graph(
                figure=px.scatter(
                    portfolio_data,
                    x='score_credito',
                    y='valor_contrato',
                    color='risco_credito',
                    title='📈 Score vs Valor do Contrato',
                    size='valor_contrato',
                    hover_data=['segmento', 'dias_atraso']
                )
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '5px'})
    ]),
    
    # Tabela
    html.Div([
        html.H3("📋 Detalhes do Portfolio", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'margin': '20px 0'}),
        dash_table.DataTable(
            data=portfolio_data.head(12).to_dict('records'),
            columns=[{"name": i, "id": i} for i in ['cliente_id', 'segmento', 'valor_contrato', 'dias_atraso', 'risco_credito', 'satisfacao_cliente', 'segmento_cliente']],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px', 'fontFamily': 'Arial'},
            style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'}
        )
    ], style={'margin': '10px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P(f"✅ Credit Control Dashboard | Branch: {BRANCH_NAME} | " 
               "💼 Demonstração para vaga Junior Data & Reporting Officer",
              style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '0.8em', 'marginTop': '20px'})
    ])
])

# Server configuration
server = app.server

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    debug = False if os.environ.get('RENDER') else True
    
    print(f"🌈 Dashboard rodando em: http://0.0.0.0:{port}")
    app.run_server(host='0.0.0.0', port=port, debug=debug)