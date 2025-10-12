from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
from src.config.database import get_async_connection

app = FastAPI(
    title="Dashboard Saúde Ocupacional - Moçambique",
    description="API para visualização de dados de saúde ocupacional",
    version="1.0.0"
)

# Tempo de início do serviço
START_TIME = datetime.now()

def get_uptime():
    """Calcula o tempo online desde o início"""
    uptime = datetime.now() - START_TIME
    days = uptime.days
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    else:
        return f"{hours}h {minutes}m"

def get_risk_emoji(nivel_risco):
    """Retorna emoji baseado no nível de risco"""
    emojis = {
        'Alto': '🔴',
        'Médio': '🟡', 
        'Baixo': '🟢'
    }
    return emojis.get(nivel_risco, '⚪')

@app.get("/")
async def root():
    return {
        "message": "Bem-vindo ao Dashboard de Saúde Ocupacional - Moçambique",
        "status": "online",
        "uptime": get_uptime(),
        "availability": "24/7/365",
        "endpoints": {
            "health": "/health",
            "risk_data": "/api/risk-data",
            "dashboard": "/dashboard"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "mozambique-health-pipeline",
        "uptime": get_uptime(),
        "availability": "24/7/365",
        "version": "1.0.0"
    }

@app.get("/api/risk-data")
async def get_risk_data():
    """Retorna dados de avaliação de risco"""
    try:
        conn = await get_async_connection()
        data = await conn.fetch("SELECT * FROM risk_assessment ORDER BY score_risco DESC")
        await conn.close()
        
        return [dict(record) for record in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados: {str(e)}")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard HTML com visualizações"""
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
        risco_alto_count = len(df[df['nivel_risco'] == 'Alto'])
        
        # Gráficos
        fig1 = px.bar(df, x='provincia', y='score_risco', color='nivel_risco',
                     title='🎯 Score de Risco por Província',
                     labels={'score_risco': 'Score de Risco', 'provincia': 'Província'},
                     color_discrete_map={'Alto': '#FF6B6B', 'Médio': '#FFD93D', 'Baixo': '#6BCF7F'})
        
        fig2 = px.pie(df, names='nivel_risco', title='📊 Distribuição de Níveis de Risco',
                     color_discrete_sequence=['#6BCF7F', '#FFD93D', '#FF6B6B'])
        
        fig3 = px.scatter(df, x='populacao_exposta', y='score_risco', 
                         size=df['score_risco'].values,
                         color='nivel_risco', 
                         hover_name='provincia',
                         title='🌍 População Exposta vs Score de Risco',
                         color_discrete_map={'Alto': '#FF6B6B', 'Médio': '#FFD93D', 'Baixo': '#6BCF7F'})
        
        html_content = f"""
        <html>
            <head>
                <title>🏥 Dashboard Saúde Ocupacional - Moçambique</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: white; padding: 30px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                    .badges {{ display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }}
                    .badge {{ background: #28a745; color: white; padding: 10px 20px; border-radius: 20px; font-weight: bold; }}
                    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                    .stat-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
                    .stat-value {{ font-size: 28px; font-weight: bold; color: #2c3e50; }}
                    .stat-label {{ font-size: 14px; color: #7f8c8d; }}
                    .chart {{ background: white; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏥 Dashboard Saúde Ocupacional - Moçambique</h1>
                        <p>📍 Monitoramento em tempo real | 🎯 Análise de riscos ocupacionais</p>
                        
                        <div class="badges">
                            <div class="badge">🟢 ONLINE 24/7/365</div>
                            <div class="badge" style="background: #007bff;">⏱️ Uptime: {get_uptime()}</div>
                            <div class="badge" style="background: #6f42c1;">🚀 Alta Performance</div>
                        </div>
                        
                        <div class="stats">
                            <div class="stat-card">
                                <div class="stat-value">{total_provincias}</div>
                                <div class="stat-label">🏙️ Províncias</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{total_populacao:,}</div>
                                <div class="stat-label">👥 População</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{score_medio:.1f}</div>
                                <div class="stat-label">📈 Score Médio</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{risco_alto_count}</div>
                                <div class="stat-label">🚨 Alertas Alto</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px;">
                        <div class="chart">{fig1.to_html(full_html=False)}</div>
                        <div class="chart">{fig2.to_html(full_html=False)}</div>
                    </div>
                    
                    <div class="chart">
                        {fig3.to_html(full_html=False)}
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px; color: #6c757d;">
                        <p>🚀 Desenvolvido com FastAPI & Plotly | 📞 Suporte 24/7</p>
                        <p>© 2024 Saúde Ocupacional Moçambique</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"<h1>❌ Erro ao carregar dashboard: {str(e)}</h1>"
