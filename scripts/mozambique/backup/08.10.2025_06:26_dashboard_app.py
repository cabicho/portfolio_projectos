# scripts/mozambique/dashboard_app.py
# O erro é porque a versão do Dash foi atualizada e o método run_server foi substituído por run
import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# Carregar ou gerar dados
def load_data():
    """Carrega dados ou gera dados de exemplo"""
    try:
        df_empresas = pd.read_csv('data/mozambique/raw/empresas.csv')
        with open('data/mozambique/reports/resultados.json', 'r') as f:
            resultados = json.load(f)
    except:
        # Dados de exemplo se não existirem
        print("Gerando dados de exemplo...")
        df_empresas, resultados = generate_sample_data()
    
    return df_empresas, resultados

def generate_sample_data():
    """Gera dados de exemplo para o dashboard"""
    np.random.seed(42)
    
    # Empresas
    empresas = []
    setores = ['Mineração', 'Agricultura', 'Construção Civil', 'Manufactura', 'Comércio', 'Serviços', 'Transportes']
    provincias = ['Maputo', 'Gaza', 'Inhambane', 'Sofala', 'Manica', 'Zambézia', 'Nampula', 'Cabo Delgado']
    
    for i in range(150):
        setor = np.random.choice(setores)
        
        # Parâmetros por setor
        parametros = {
            'Mineração': {'risco': 8.0, 'burnout': 4.2, 'prod_base': 70, 'roi_base': 25},
            'Agricultura': {'risco': 7.0, 'burnout': 3.8, 'prod_base': 60, 'roi_base': 18},
            'Construção Civil': {'risco': 8.5, 'burnout': 4.1, 'prod_base': 65, 'roi_base': 22},
            'Manufactura': {'risco': 6.5, 'burnout': 3.9, 'prod_base': 75, 'roi_base': 28},
            'Comércio': {'risco': 4.0, 'burnout': 3.2, 'prod_base': 80, 'roi_base': 35},
            'Serviços': {'risco': 3.5, 'burnout': 3.5, 'prod_base': 85, 'roi_base': 32},
            'Transportes': {'risco': 7.5, 'burnout': 4.0, 'prod_base': 70, 'roi_base': 20}
        }
        
        param = parametros.get(setor, {'risco': 5.0, 'burnout': 3.5, 'prod_base': 70, 'roi_base': 25})
        
        empresa = {
            'empresa_id': i + 1,
            'setor': setor,
            'provincia': np.random.choice(provincias),
            'tamanho': np.random.choice(['Pequena', 'Média', 'Grande'], p=[0.6, 0.3, 0.1]),
            'invest_ergonomia': max(10000, np.random.normal(50000, 20000)),
            'invest_saude_mental': max(5000, np.random.normal(25000, 10000)),
            'burnout_medio': max(1, min(7, np.random.normal(param['burnout'], 0.6))),
            'acidentes_ano': max(0, np.random.poisson(param['risco'])),
            'produtividade': max(20, np.random.normal(param['prod_base'], 15)),
            'lucratividade_mil': max(50, np.random.normal(400, 150)),
            'turnover': max(5, np.random.normal(18, 6)),
            'satisfacao': max(1, min(10, np.random.normal(6.8, 1.3)))
        }
        empresas.append(empresa)
    
    df_empresas = pd.DataFrame(empresas)
    
    # Calcular ROI
    df_empresas['invest_total'] = df_empresas['invest_ergonomia'] + df_empresas['invest_saude_mental']
    df_empresas['custo_acidentes'] = df_empresas['acidentes_ano'] * 7500
    df_empresas['roi'] = ((df_empresas['lucratividade_mil'] * 1000 - df_empresas['custo_acidentes'] - df_empresas['invest_total']) / 
                         df_empresas['invest_total'] * 100)
    
    # Resultados
    resultados = {
        'total_empresas': len(df_empresas),
        'roi_medio': float(df_empresas['roi'].mean()),
        'burnout_medio': float(df_empresas['burnout_medio'].mean()),
        'produtividade_media': float(df_empresas['produtividade'].mean()),
        'acidentes_medio': float(df_empresas['acidentes_ano'].mean()),
        'investimento_total_medio': float(df_empresas['invest_total'].mean())
    }
    
    return df_empresas, resultados

# Inicializar dados
df_empresas, resultados = load_data()

# Criar app Dash
app = dash.Dash(__name__, title="Dashboard SSO Moçambique")

# Layout do dashboard
app.layout = html.Div([
    # Cabeçalho
    html.Div([
        html.H1("🇲🇿 Dashboard SSO - Moçambique", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Análise de Ergonomia, Saúde Mental e Performance Financeira", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px'}),
        html.Hr()
    ]),
    
    # Filtros
    html.Div([
        html.Div([
            html.Label("🏭 Setor:"),
            dcc.Dropdown(
                id='filtro-setor',
                options=[{'label': 'Todos', 'value': 'Todos'}] + 
                        [{'label': setor, 'value': setor} for setor in sorted(df_empresas['setor'].unique())],
                value='Todos',
                clearable=False
            )
        ], className='four columns'),
        
        html.Div([
            html.Label("🗺️ Província:"),
            dcc.Dropdown(
                id='filtro-provincia',
                options=[{'label': 'Todas', 'value': 'Todas'}] + 
                        [{'label': prov, 'value': prov} for prov in sorted(df_empresas['provincia'].unique())],
                value='Todas',
                clearable=False
            )
        ], className='four columns'),
        
        html.Div([
            html.Label("🏢 Tamanho:"),
            dcc.Dropdown(
                id='filtro-tamanho',
                options=[{'label': 'Todos', 'value': 'Todos'}] + 
                        [{'label': tam, 'value': tam} for tam in sorted(df_empresas['tamanho'].unique())],
                value='Todos',
                clearable=False
            )
        ], className='four columns'),
    ], className='row', style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
    
    # KPIs Principais
    html.Div([
        html.Div([
            html.Div([
                html.H3(id='kpi-roi', children=f"{resultados['roi_medio']:.1f}%", 
                       style={'color': '#27ae60', 'fontSize': '32px', 'margin': '0'}),
                html.P("📈 ROI Médio SSO", style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
            ], className='kpi-card')
        ], className='three columns'),
        
        html.Div([
            html.Div([
                html.H3(id='kpi-burnout', children=f"{resultados['burnout_medio']:.2f}", 
                       style={'color': '#e74c3c', 'fontSize': '32px', 'margin': '0'}),
                html.P("🔥 Burnout Médio", style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
            ], className='kpi-card')
        ], className='three columns'),
        
        html.Div([
            html.Div([
                html.H3(id='kpi-produtividade', children=f"{resultados['produtividade_media']:.1f}", 
                       style={'color': '#3498db', 'fontSize': '32px', 'margin': '0'}),
                html.P("⚡ Produtividade Média", style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
            ], className='kpi-card')
        ], className='three columns'),
        
        html.Div([
            html.Div([
                html.H3(id='kpi-empresas', children=f"{resultados['total_empresas']}", 
                       style={'color': '#9b59b6', 'fontSize': '32px', 'margin': '0'}),
                html.P("🏢 Empresas Analisadas", style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
            ], className='kpi-card')
        ], className='three columns'),
    ], className='row', style={'marginBottom': '30px'}),
    
    # Primeira linha de gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-roi-setor')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='grafico-burnout-setor')
        ], className='six columns'),
    ], className='row'),
    
    # Segunda linha de gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-correlacao')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='grafico-investimento-return')
        ], className='six columns'),
    ], className='row'),
    
    # Terceira linha de gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-regional')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='grafico-tamanho-impacto')
        ], className='six columns'),
    ], className='row'),
    
    # Quarta linha - Análise detalhada
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-setor-detalhado')
        ], className='twelve columns'),
    ], className='row'),
    
    # Rodapé
    html.Div([
        html.Hr(),
        html.P(f"🇲🇿 Sistema de Análise SSO Moçambique | Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
               style={'textAlign': 'center', 'color': '#95a5a6', 'fontSize': '12px'})
    ], style={'marginTop': '40px'})
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})

# Callbacks para interatividade
@app.callback(
    [Output('kpi-roi', 'children'),
     Output('kpi-burnout', 'children'),
     Output('kpi-produtividade', 'children'),
     Output('kpi-empresas', 'children'),
     Output('grafico-roi-setor', 'figure'),
     Output('grafico-burnout-setor', 'figure'),
     Output('grafico-correlacao', 'figure'),
     Output('grafico-investimento-return', 'figure'),
     Output('grafico-regional', 'figure'),
     Output('grafico-tamanho-impacto', 'figure'),
     Output('grafico-setor-detalhado', 'figure')],
    [Input('filtro-setor', 'value'),
     Input('filtro-provincia', 'value'),
     Input('filtro-tamanho', 'value')]
)
def update_dashboard(setor_selecionado, provincia_selecionada, tamanho_selecionado):
    # Aplicar filtros
    df_filtrado = df_empresas.copy()
    
    if setor_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['setor'] == setor_selecionado]
    
    if provincia_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['provincia'] == provincia_selecionada]
    
    if tamanho_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tamanho'] == tamanho_selecionado]
    
    # Calcular KPIs atualizados
    kpi_roi = f"{df_filtrado['roi'].mean():.1f}%"
    kpi_burnout = f"{df_filtrado['burnout_medio'].mean():.2f}"
    kpi_produtividade = f"{df_filtrado['produtividade'].mean():.1f}"
    kpi_empresas = f"{len(df_filtrado)}"
    
    # 1. Gráfico ROI por Setor
    fig_roi_setor = px.box(df_filtrado, x='setor', y='roi',
                          title='📊 Distribuição do ROI por Setor',
                          color='setor',
                          color_discrete_sequence=px.colors.qualitative.Set3)
    fig_roi_setor.update_layout(showlegend=False, xaxis_title="Setor", yaxis_title="ROI (%)")
    
    # 2. Gráfico Burnout por Setor
    burnout_setor = df_filtrado.groupby('setor')['burnout_medio'].mean().reset_index()
    fig_burnout_setor = px.bar(burnout_setor, x='setor', y='burnout_medio',
                              title='🔥 Burnout Médio por Setor',
                              color='burnout_medio',
                              color_continuous_scale='Reds')
    fig_burnout_setor.update_layout(xaxis_title="Setor", yaxis_title="Burnout (1-7)")
    
    # 3. Gráfico de Correlação
    fig_correlacao = px.scatter(df_filtrado, x='burnout_medio', y='produtividade',
                               color='setor', size='invest_total',
                               title='🔗 Correlação: Burnout vs Produtividade',
                               trendline='ols',
                               hover_data=['empresa_id', 'tamanho'])
    fig_correlacao.update_layout(xaxis_title="Burnout Médio", yaxis_title="Produtividade")
    
    # 4. Gráfico Investimento vs Retorno
    fig_invest_return = px.scatter(df_filtrado, x='invest_total', y='roi',
                                  color='acidentes_ano', size='lucratividade_mil',
                                  title='💰 Investimento Total vs ROI',
                                  hover_data=['setor', 'provincia'],
                                  color_continuous_scale='Viridis')
    fig_invest_return.update_layout(xaxis_title="Investimento Total (€)", yaxis_title="ROI (%)")
    
    # 5. Gráfico Regional
    regional_data = df_filtrado.groupby('provincia').agg({
        'roi': 'mean',
        'burnout_medio': 'mean',
        'produtividade': 'mean'
    }).reset_index()
    
    fig_regional = make_subplots(
        rows=1, cols=3,
        subplot_titles=('ROI por Província', 'Burnout por Província', 'Produtividade por Província'),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    fig_regional.add_trace(go.Bar(x=regional_data['provincia'], y=regional_data['roi'], 
                                 name='ROI', marker_color='#27ae60'), 1, 1)
    fig_regional.add_trace(go.Bar(x=regional_data['provincia'], y=regional_data['burnout_medio'],
                                 name='Burnout', marker_color='#e74c3c'), 1, 2)
    fig_regional.add_trace(go.Bar(x=regional_data['provincia'], y=regional_data['produtividade'],
                                 name='Produtividade', marker_color='#3498db'), 1, 3)
    
    fig_regional.update_layout(height=400, title_text="📍 Análise Regional por Província", showlegend=False)
    
    # 6. Gráfico Impacto por Tamanho
    tamanho_impacto = df_filtrado.groupby('tamanho').agg({
        'roi': 'mean',
        'burnout_medio': 'mean',
        'invest_total': 'mean'
    }).reset_index()
    
    fig_tamanho = make_subplots(
        rows=1, cols=3,
        subplot_titles=('ROI por Tamanho', 'Burnout por Tamanho', 'Investimento por Tamanho'),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    fig_tamanho.add_trace(go.Bar(x=tamanho_impacto['tamanho'], y=tamanho_impacto['roi'],
                                name='ROI', marker_color='#2ecc71'), 1, 1)
    fig_tamanho.add_trace(go.Bar(x=tamanho_impacto['tamanho'], y=tamanho_impacto['burnout_medio'],
                                name='Burnout', marker_color='#e74c3c'), 1, 2)
    fig_tamanho.add_trace(go.Bar(x=tamanho_impacto['tamanho'], y=tamanho_impacto['invest_total'],
                                name='Investimento', marker_color='#3498db'), 1, 3)
    
    fig_tamanho.update_layout(height=400, title_text="🏢 Impacto do Tamanho da Empresa", showlegend=False)
    
    # 7. Gráfico Setorial Detalhado
    setor_detalhado = df_filtrado.groupby('setor').agg({
        'roi': 'mean',
        'burnout_medio': 'mean',
        'produtividade': 'mean',
        'acidentes_ano': 'mean',
        'invest_total': 'mean',
        'satisfacao': 'mean'
    }).reset_index()
    
    fig_setor_detalhado = go.Figure(data=[
        go.Bar(name='ROI', x=setor_detalhado['setor'], y=setor_detalhado['roi'], yaxis='y1', offsetgroup=1),
        go.Bar(name='Burnout', x=setor_detalhado['setor'], y=setor_detalhado['burnout_medio'], yaxis='y2', offsetgroup=2),
        go.Bar(name='Produtividade', x=setor_detalhado['setor'], y=setor_detalhado['produtividade'], yaxis='y3', offsetgroup=3)
    ])
    
    fig_setor_detalhado.update_layout(
        title='📈 Análise Setorial Detalhada - Múltiplas Métricas',
        xaxis=dict(title='Setor'),
        yaxis=dict(title='ROI (%)', side='left', showgrid=False),
        yaxis2=dict(title='Burnout (1-7)', side='right', overlaying='y', showgrid=False),
        yaxis3=dict(title='Produtividade', side='right', overlaying='y', showgrid=False, position=0.85),
        barmode='group'
    )
    
    return (kpi_roi, kpi_burnout, kpi_produtividade, kpi_empresas,
            fig_roi_setor, fig_burnout_setor, fig_correlacao, fig_invest_return,
            fig_regional, fig_tamanho, fig_setor_detalhado)

# CSS personalizado
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .kpi-card {
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 5px solid #3498db;
                transition: transform 0.3s ease;
            }
            .kpi-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            }
            .kpi-card h3 {
                margin: 0;
                font-size: 28px;
                font-weight: bold;
            }
            .kpi-card p {
                margin: 8px 0 0 0;
                color: #7f8c8d;
                font-size: 14px;
                font-weight: 500;
            }
            body {
                background-color: #f8f9fa;
                margin: 0;
                padding: 0;
            }
            .row {
                margin-bottom: 25px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    # Garantir que os diretórios existam
    os.makedirs('data/mozambique/raw', exist_ok=True)
    os.makedirs('data/mozambique/reports', exist_ok=True)
    
    print("🚀 Iniciando Dashboard SSO Moçambique...")
    print("📊 Acesse: http://localhost:8050")
    print("🇲🇿 Analisando dados de ergonomia e saúde mental")
    
    app.run_server(host='0.0.0.0', port=8050, debug=True)