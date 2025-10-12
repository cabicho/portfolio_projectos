from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from src.config.database import get_async_connection

app = FastAPI(
    title="Dashboard Saúde Ocupacional - Moçambique",
    description="API para visualização de dados de saúde ocupacional",
    version="1.0.0"
)

START_TIME = datetime.now()

def get_uptime():
    uptime = datetime.now() - START_TIME
    days = uptime.days
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"

def get_risk_emoji(nivel_risco):
    emojis = {'Alto': '🔴', 'Médio': '🟡', 'Baixo': '🟢'}
    return emojis.get(nivel_risco, '⚪')

@app.get("/")
async def root():
    return {"message": "Bem-vindo ao Dashboard", "status": "online", "uptime": get_uptime()}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "uptime": get_uptime()}

@app.get("/api/risk-data")
async def get_risk_data():
    try:
        conn = await get_async_connection()
        data = await conn.fetch("SELECT * FROM risk_assessment ORDER BY score_risco DESC")
        await conn.close()
        return [dict(record) for record in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    try:
        conn = await get_async_connection()
        risk_data = await conn.fetch("SELECT * FROM risk_assessment ORDER BY score_risco DESC")
        await conn.close()
        
        if not risk_data:
            return "<h1>📊 Dados não disponíveis</h1>"
        
        df = pd.DataFrame([dict(record) for record in risk_data])
        df['score_risco'] = pd.to_numeric(df['score_risco'], errors='coerce')
        df['populacao_exposta'] = pd.to_numeric(df['populacao_exposta'], errors='coerce')
        df['risco_emoji'] = df['nivel_risco'].apply(get_risk_emoji)
        
        # Métricas
        total_provincias = len(df)
        total_populacao = df['populacao_exposta'].sum()
        score_medio = df['score_risco'].mean()
        
        # Distribuição por nível de risco
        dist_risco = df.groupby('nivel_risco').agg({
            'populacao_exposta': 'sum',
            'provincia': 'count'
        }).reset_index()
        dist_risco['percentual'] = (dist_risco['populacao_exposta'] / total_populacao * 100).round(1)
        
        # Gráfico de distribuição CORRIGIDO
        fig_dist = px.bar(dist_risco, x='nivel_risco', y='populacao_exposta',
                         title='👥 DISTRIBUIÇÃO DA POPULAÇÃO POR NÍVEL DE RISCO',
                         labels={'populacao_exposta': 'População', 'nivel_risco': 'Nível de Risco'},
                         color='nivel_risco',
                         color_discrete_map={'Alto': '#FF6B6B', 'Médio': '#FFD93D', 'Baixo': '#6BCF7F'})
        fig_dist.update_traces(texttemplate='%{y:,}', textposition='outside')
        
        # Gráfico de pizza para distribuição
        fig_pizza = px.pie(dist_risco, values='populacao_exposta', names='nivel_risco',
                          title='📊 Percentual da População por Nível de Risco')
        
        html_content = f"""
        <html>
            <head>
                <title>Dashboard Saúde - Moçambique</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    .chart {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                    .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
                    .stat-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏥 Distribuição da População por Risco</h1>
                        <div class="stats">
                            <div class="stat-card">
                                <div style="font-size: 24px; font-weight: bold;">{total_provincias}</div>
                                <div>Províncias</div>
                            </div>
                            <div class="stat-card">
                                <div style="font-size: 24px; font-weight: bold;">{total_populacao:,}</div>
                                <div>População Total</div>
                            </div>
                            <div class="stat-card">
                                <div style="font-size: 24px; font-weight: bold;">{score_medio:.1f}</div>
                                <div>Score Médio</div>
                            </div>
                            <div class="stat-card">
                                <div style="font-size: 24px; font-weight: bold;">{get_uptime()}</div>
                                <div>Uptime</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="grid">
                        <div class="chart">
                            {fig_dist.to_html(full_html=False)}
                        </div>
                        <div class="chart">
                            {fig_pizza.to_html(full_html=False)}
                        </div>
                    </div>
                    
                    <div class="chart">
                        <h3>📋 Detalhes da Distribuição</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr style="background: #667eea; color: white;">
                                <th style="padding: 10px;">Nível Risco</th>
                                <th style="padding: 10px;">Províncias</th>
                                <th style="padding: 10px;">População</th>
                                <th style="padding: 10px;">Percentual</th>
                            </tr>
                            {"".join([f"""
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{get_risk_emoji(row['nivel_risco'])} {row['nivel_risco']}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{int(row['provincia'])}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{row['populacao_exposta']:,}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{row['percentual']}%</td>
                            </tr>
                            """ for _, row in dist_risco.iterrows()])}
                        </table>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"<h1>❌ Erro: {str(e)}</h1>"
