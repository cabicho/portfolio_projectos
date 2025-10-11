from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from config.database import get_async_connection

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
        
        # Criar gráficos
        fig1 = px.bar(df, x='provincia', y='score_risco', color='nivel_risco',
                     title='Score de Risco por Província')
        
        fig2 = px.pie(df, names='nivel_risco', title='Distribuição de Níveis de Risco')
        
        fig3 = px.scatter(df, x='populacao_exposta', y='score_risco', 
                         size='score_risco', color='nivel_risco', hover_name='provincia',
                         title='População Exposta vs Score de Risco')
        
        html_content = f"""
        <html>
            <head>
                <title>Dashboard Saúde Ocupacional - Moçambique</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .chart {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1>🏥 Dashboard Saúde Ocupacional - Moçambique</h1>
                <p>Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                
                <div class="chart">{fig1.to_html(full_html=False)}</div>
                <div class="chart">{fig2.to_html(full_html=False)}</div>
                <div class="chart">{fig3.to_html(full_html=False)}</div>
            </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"<h1>Erro ao carregar dashboard: {str(e)}</h1>"
