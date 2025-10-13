# pipeline-saude-mocambique/src/api/dashboard.py
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
        
        # Distribuição por nível de risco
        dist_risco = df.groupby('nivel_risco').agg({
            'populacao_exposta': 'sum',
            'provincia': 'count'
        }).reset_index()
        dist_risco['percentual'] = (dist_risco['populacao_exposta'] / total_populacao * 100).round(1)
        
        # Gráfico 1: Score de Risco por Província
        fig1 = px.bar(df, x='provincia', y='score_risco', color='nivel_risco',
                     title='🎯 Score de Risco por Província',
                     labels={'score_risco': 'Score de Risco', 'provincia': 'Província'},
                     color_discrete_map={'Alto': '#FF6B6B', 'Médio': '#FFD93D', 'Baixo': '#6BCF7F'})
        fig1.update_layout(xaxis_tickangle=-45)
        
        # Gráfico 2: Distribuição de Níveis de Risco
        fig2 = px.pie(df, names='nivel_risco', title='📊 Distribuição de Níveis de Risco',
                     color_discrete_sequence=['#6BCF7F', '#FFD93D', '#FF6B6B'])
        
        # Gráfico 3: População vs Score de Risco
        fig3 = px.scatter(df, x='populacao_exposta', y='score_risco', 
                         size=df['score_risco'].values,
                         color='nivel_risco', 
                         hover_name='provincia',
                         title='🌍 População Exposta vs Score de Risco',
                         color_discrete_map={'Alto': '#FF6B6B', 'Médio': '#FFD93D', 'Baixo': '#6BCF7F'})
        
        # Gráfico 4: Distribuição da População por Nível de Risco
        fig4 = px.bar(dist_risco, x='nivel_risco', y='populacao_exposta',
                     title='👥 Distribuição da População por Nível de Risco',
                     labels={'populacao_exposta': 'População Exposta', 'nivel_risco': 'Nível de Risco'},
                     color='nivel_risco',
                     color_discrete_map={'Alto': '#FF6B6B', 'Médio': '#FFD93D', 'Baixo': '#6BCF7F'})
        fig4.update_traces(texttemplate='%{y:,}', textposition='outside')
        
        # Gerar HTML para a tabela de distribuição
        tabela_distribuicao = ""
        for _, row in dist_risco.iterrows():
            tabela_distribuicao += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{get_risk_emoji(row['nivel_risco'])} {row['nivel_risco']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{int(row['provincia'])}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{row['populacao_exposta']:,}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{row['percentual']}%</td>
            </tr>
            """
        
        # Gerar HTML para o ranking de províncias
        ranking_provincias = ""
        for _, row in df.iterrows():
            ranking_provincias += f"""
            <div style="background: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1); border-left: 4px solid {'#FF6B6B' if row['nivel_risco'] == 'Alto' else '#FFD93D' if row['nivel_risco'] == 'Médio' else '#6BCF7F'};">
                <div style="font-size: 24px; margin-bottom: 5px;">{row['risco_emoji']}</div>
                <div style="font-weight: bold; color: #2c3e50; font-size: 16px;">{row['provincia']}</div>
                <div style="color: #7f8c8d; font-size: 14px; margin: 5px 0;">👥 {row['populacao_exposta']:,}</div>
                <div style="color: #e74c3c; font-size: 13px; font-weight: bold;">Score: {row['score_risco']}</div>
                <div style="color: #95a5a6; font-size: 12px;">{row['nivel_risco']}</div>
            </div>
            """
        
        html_content = f"""
        <html>
            <head>
                <title>🏥 Dashboard Saúde Ocupacional - Moçambique</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        margin: 0; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }}
                    .container {{ 
                        max-width: 1400px; 
                        margin: 0 auto; 
                        padding: 20px;
                    }}
                    .header {{ 
                        background: rgba(255, 255, 255, 0.95); 
                        padding: 30px; 
                        border-radius: 20px; 
                        margin-bottom: 25px; 
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    }}
                    .status-badges {{
                        display: flex;
                        gap: 15px;
                        margin: 20px 0;
                        flex-wrap: wrap;
                    }}
                    .badge {{
                        background: linear-gradient(45deg, #00b09b, #96c93d);
                        color: white;
                        padding: 10px 20px;
                        border-radius: 25px;
                        font-weight: bold;
                        font-size: 14px;
                    }}
                    .stats {{ 
                        display: grid; 
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                        gap: 20px; 
                        margin-bottom: 30px;
                    }}
                    .stat-card {{ 
                        background: rgba(255, 255, 255, 0.95);
                        padding: 25px; 
                        border-radius: 15px; 
                        text-align: center; 
                        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                    }}
                    .stat-value {{ 
                        font-size: 32px; 
                        font-weight: bold; 
                        color: #2c3e50; 
                        margin: 10px 0;
                    }}
                    .stat-label {{ 
                        font-size: 14px; 
                        color: #7f8c8d; 
                        font-weight: 600;
                    }}
                    .chart {{ 
                        background: rgba(255, 255, 255, 0.95); 
                        padding: 25px; 
                        border-radius: 15px; 
                        margin-bottom: 25px; 
                        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                    }}
                    .grid-2col {{
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 25px;
                    }}
                    .distribution-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                        background: white;
                        border-radius: 10px;
                        overflow: hidden;
                    }}
                    .distribution-table th,
                    .distribution-table td {{
                        padding: 12px 15px;
                        text-align: left;
                        border-bottom: 1px solid #e0e0e0;
                    }}
                    .distribution-table th {{
                        background: #667eea;
                        color: white;
                        font-weight: 600;
                    }}
                    .province-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                        margin-top: 20px;
                    }}
                    @media (max-width: 768px) {{
                        .grid-2col {{
                            grid-template-columns: 1fr;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏥 Dashboard Saúde Ocupacional - Moçambique</h1>
                        <div class="status-badges">
                            <div class="badge">🟢 ONLINE 24/7/365</div>
                            <div class="badge">⏱️ Uptime: {get_uptime()}</div>
                            <div class="badge">📊 {total_provincias} Províncias</div>
                        </div>
                        
                        <div class="stats">
                            <div class="stat-card">
                                <div class="stat-value">{total_provincias}</div>
                                <div class="stat-label">Províncias Monitoradas</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{total_populacao:,}</div>
                                <div class="stat-label">População Total Exposta</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{score_medio:.1f}</div>
                                <div class="stat-label">Score Médio de Risco</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{risco_alto_count}</div>
                                <div class="stat-label">Alertas de Risco Alto</div>
                            </div>
                        </div>
                    </div>

                    <div class="grid-2col">
                        <div class="chart">{fig1.to_html(full_html=False)}</div>
                        <div class="chart">{fig2.to_html(full_html=False)}</div>
                    </div>

                    <div class="chart">
                        {fig3.to_html(full_html=False)}
                    </div>

                    <div class="chart">
                        {fig4.to_html(full_html=False)}
                    </div>

                    <div class="chart">
                        <h3>📋 Distribuição Detalhada da População por Nível de Risco</h3>
                        <table class="distribution-table">
                            <thead>
                                <tr>
                                    <th>Nível de Risco</th>
                                    <th>Nº de Províncias</th>
                                    <th>População Exposta</th>
                                    <th>Percentual</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tabela_distribuicao}
                                <tr style="background: #f8f9fa; font-weight: bold;">
                                    <td>📊 TOTAL</td>
                                    <td>{total_provincias}</td>
                                    <td>{total_populacao:,}</td>
                                    <td>100%</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="chart">
                        <h3>🎯 Ranking de Províncias por Risco</h3>
                        <div class="province-grid">
                            {ranking_provincias}
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px; color: white;">
                        <p>🚀 Desenvolvido com FastAPI & Plotly | 📞 Suporte 24/7</p>
                        <p>© 2024 Saúde Ocupacional Moçambique</p>
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
# Crie uma função auxiliar ou variável separada
def format_sample_indicator(source):
    if source.get('indicators_sample'):
        sample_html = "<p><strong>Amostra:</strong><br>" + "<br>".join([
            f"• {ind['indicador_nome']} ({ind['ano']}): {ind['valor']}" 
            for ind in source.get('indicators_sample', [])[:2]
        ]) + "</p>"
        return sample_html
    return ""

# Adicionar ao pipeline-saude-mocambique/src/api/dashboard.py
from src.verify.data_sources_verification import DataSourcesVerification
    
# Adicionar este endpoint ao app FastAPI
@app.get("/api/verify-dashboard")
async def verification_dashboard():
    """Dashboard de verificação das fontes de dados"""
    try:
        verifier = DataSourcesVerification()
        report = await verifier.verify_all_sources()
        
        # Criar visualização HTML do relatório
        # Primeiro, gere o conteúdo das fontes separadamente
        sources_html = "".join([f""" 
        <div class="source-card {'status-active' if source['status'] == '✅ ATIVA' else 'status-inactive'}">
            <h3>{name.upper()}</h3>
            <p><strong>Status:</strong> {source['status']}</p>
            <p><strong>Registros:</strong> {source['total_records']}</p>
            <p><strong>Tipo:</strong> {source['source_type']}</p>
            <p><strong>Qualidade:</strong> {source.get('data_quality', 'N/A')}</p>
            {format_sample_indicator(source) if 'format_sample_indicator' in locals() else ''}
        </div>
        """ for name, source in report['sources'].items()])

        # Agora use no HTML principal
        html_content = f"""
        <html>
            <head>
                <title>Verificação de Fontes - SST Moçambique</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    .source-card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; }}
                    .status-active {{ border-left: 5px solid #28a745; }}
                    .status-inactive {{ border-left: 5px solid #dc3545; }}
                    .status-error {{ border-left: 5px solid #ffc107; }}
                    .badge {{ padding: 5px 10px; border-radius: 15px; color: white; font-size: 12px; }}
                    .badge-success {{ background: #28a745; }}
                    .badge-warning {{ background: #ffc107; }}
                    .badge-danger {{ background: #dc3545; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔍 Verificação de Fontes de Dados SST</h1>
                        <p>Status Geral: <span class="badge badge-{'success' if report['summary']['overall_status'] == '✅ EXCELENTE' else 'warning' if report['summary']['overall_status'] == '⚠️  REGULAR' else 'danger'}">{report['summary']['overall_status']}</span></p>
                        <p>Fontes Ativas: {report['summary']['sources_with_data']}/{report['summary']['total_sources']}</p>
                        <p>Total de Registros: {report['summary']['total_records']}</p>
                    </div>
                    
                    {sources_html}
                </div>
            </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Erro na verificação: {str(e)}</h1>")