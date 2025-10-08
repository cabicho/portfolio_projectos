# scripts/mozambique/dashboard_app.py
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

print("🚀 Iniciando Dashboard SSO Moçambique...")

# Gerar dados de exemplo diretamente
def generate_data():
    np.random.seed(42)
    
    empresas = []
    setores = ['Mineração', 'Agricultura', 'Construção Civil', 'Manufactura', 'Comércio', 'Serviços']
    provincias = ['Maputo', 'Gaza', 'Inhambane', 'Sofala', 'Manica', 'Nampula']
    
    for i in range(100):
        setor = np.random.choice(setores)
        empresa = {
            'empresa_id': i + 1,
            'setor': setor,
            'provincia': np.random.choice(provincias),
            'invest_ergonomia': max(10000, np.random.normal(50000, 20000)),
            'invest_saude_mental': max(5000, np.random.normal(25000, 10000)),
            'burnout_medio': max(1, min(7, np.random.normal(3.5, 0.8))),
            'produtividade': max(20, np.random.normal(70, 15)),
            'lucratividade_mil': max(50, np.random.normal(300, 100)),
        }
        empresas.append(empresa)
    
    df = pd.DataFrame(empresas)
    df['invest_total'] = df['invest_ergonomia'] + df['invest_saude_mental']
    df['roi'] = ((df['lucratividade_mil'] * 1000 - df['invest_total']) / df['invest_total'] * 100)
    
    return df

# Carregar dados
df_empresas = generate_data()

# Criar app Dash
app = dash.Dash(__name__)

# Layout simples e funcional
app.layout = html.Div([
    html.H1("🇲🇿 Dashboard SSO - Moçambique", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
    
    # KPIs
    html.Div([
        html.Div([
            html.H3(f"{df_empresas['roi'].mean():.1f}%", style={'color': '#27ae60'}),
            html.P("📈 ROI Médio")
        ], style={'textAlign': 'center', 'padding': '20px', 'background': 'white', 'margin': '10px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3(f"{df_empresas['burnout_medio'].mean():.2f}", style={'color': '#e74c3c'}),
            html.P("🔥 Burnout Médio")
        ], style={'textAlign': 'center', 'padding': '20px', 'background': 'white', 'margin': '10px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3(f"{df_empresas['produtividade'].mean():.1f}", style={'color': '#3498db'}),
            html.P("⚡ Produtividade Média")
        ], style={'textAlign': 'center', 'padding': '20px', 'background': 'white', 'margin': '10px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3(f"{len(df_empresas)}", style={'color': '#9b59b6'}),
            html.P("🏢 Empresas")
        ], style={'textAlign': 'center', 'padding': '20px', 'background': 'white', 'margin': '10px', 'borderRadius': '10px'}),
    ], style={'display': 'flex', 'justifyContent': 'center'}),
    
    # Gráficos
    html.Div([
        dcc.Graph(
            figure=px.box(df_empresas, x='setor', y='roi', 
                         title='ROI por Setor em Moçambique')
        )
    ]),
    
    html.Div([
        dcc.Graph(
            figure=px.scatter(df_empresas, x='burnout_medio', y='produtividade',
                            color='setor', title='Relação Burnout vs Produtividade')
        )
    ]),
    
    html.Div([
        dcc.Graph(
            figure=px.bar(df_empresas.groupby('setor')['burnout_medio'].mean().reset_index(),
                         x='setor', y='burnout_medio',
                         title='Burnout Médio por Setor',
                         color='burnout_medio')
        )
    ]),
    
    html.P(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
           style={'textAlign': 'center', 'color': '#95a5a6', 'marginTop': '40px'})
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f8f9fa'})

if __name__ == '__main__':
    print("📊 Dashboard rodando em: http://localhost:8050")
    print("🇲🇿 Dados de exemplo carregados com sucesso!")
    app.run(host='0.0.0.0', port=8050, debug=False)  # CORREÇÃO AQUI: run_server -> run