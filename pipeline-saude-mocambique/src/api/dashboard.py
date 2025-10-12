# pipeline-saude-mocambique/src/api/dashboard.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from src.config.database import get_async_connection

app = FastAPI(
    title="Dashboard Saúde Ocupacional - Moçambique",
    description="API para visualização de dados de saúde ocupacional",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Bem-vindo ao Dashboard de Saúde Ocupacional - Moçambique",
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
        "service": "mozambique-health-pipeline"
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
        # Buscar dados
        conn = await get_async_connection()
        risk_data = await conn.fetch("SELECT * FROM risk_assessment ORDER BY score_risco DESC")
        await conn.close()
        
        if not risk_data:
            return "<h1>Dados não disponíveis</h1>"
        
        # Converter para DataFrame
        df = pd.DataFrame([dict(record) for record in risk_data])
        
        # Garantir que as colunas numéricas sejam do tipo correto
        df['score_risco'] = pd.to_numeric(df['score_risco'], errors='coerce')
        df['populacao_exposta'] = pd.to_numeric(df['populacao_exposta'], errors='coerce')
        
        # Criar gráficos
        fig1 = px.bar(df, x='provincia', y='score_risco', color='nivel_risco',
                     title='Score de Risco por Província',
                     labels={'score_risco': 'Score de Risco', 'provincia': 'Província'})
        
        fig2 = px.pie(df, names='nivel_risco', title='Distribuição de Níveis de Risco',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        
        # CORREÇÃO: Usar valores numéricos para size, não a Series
        fig3 = px.scatter(df, x='populacao_exposta', y='score_risco', 
                         size=df['score_risco'].values,  # Usar .values para array numpy
                         color='nivel_risco', 
                         hover_name='provincia',
                         title='População Exposta vs Score de Risco',
                         labels={
                             'populacao_exposta': 'População Exposta',
                             'score_risco': 'Score de Risco',
                             'nivel_risco': 'Nível de Risco'
                         })
        
        # Adicionar gráfico extra para mais insights
        fig4 = px.treemap(df, path=['nivel_risco', 'provincia'], values='populacao_exposta',
                         title='Distribuição da População por Nível de Risco e Província',
                         color='score_risco', color_continuous_scale='RdYlGn_r')
        
        html_content = f"""
        <html>
            <head>
                <title>Dashboard Saúde Ocupacional - Moçambique</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .chart {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    h1 {{ color: #2c3e50; margin: 0; }}
                    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
                    .stat-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .stat-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
                    .stat-label {{ font-size: 14px; color: #7f8c8d; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏥 Dashboard Saúde Ocupacional - Moçambique</h1>
                        <p>Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-value">{len(df)}</div>
                            <div class="stat-label">Províncias</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{df['populacao_exposta'].sum():,}</div>
                            <div class="stat-label">População Total Exposta</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{df['score_risco'].mean():.1f}</div>
                            <div class="stat-label">Score Médio de Risco</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{len(df[df['nivel_risco'] == 'Alto'])}</div>
                            <div class="stat-label">Províncias com Risco Alto</div>
                        </div>
                    </div>
                    
                    <div class="chart" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>{fig1.to_html(full_html=False)}</div>
                        <div>{fig2.to_html(full_html=False)}</div>
                    </div>
                    
                    <div class="chart">
                        {fig3.to_html(full_html=False)}
                    </div>
                    
                    <div class="chart">
                        {fig4.to_html(full_html=False)}
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"""
        <html>
            <head><title>Erro</title></head>
            <body>
                <h1>Erro ao carregar dashboard</h1>
                <p>Detalhes: {str(e)}</p>
                <p><a href="/">Voltar para a página inicial</a></p>
            </body>
        </html>
        """