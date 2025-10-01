from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
from datetime import datetime
import logging
import json

# Configuração para Render
RENDER = os.getenv('RENDER', False)
GITHUB_REPO = os.getenv('GITHUB_REPO', 'https://github.com/cabicho/portfolio_projectos/tree/sst-dashboard/sst-dashboard-render')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SST Prediction API - Cabicho Portfolio",
    description="API para predição de métricas de Saúde e Segurança no Trabalho",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de dados
class TurnoverPredictionRequest(BaseModel):
    overtime_hours: float
    burnout_score: float
    training_hours: float
    tenure_years: float

class ROICalculationRequest(BaseModel):
    investment: float
    cost_reduction: float
    productivity_gain: float
    employees_count: int

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    environment: str
    github_repo: str

# Funções de predição
def predict_turnover(overtime: float, burnout: float, training: float, tenure: float) -> float:
    """Modelo preditivo de turnover"""
    try:
        risk_score = (overtime * 0.3 + burnout * 0.4 - training * 0.2 - tenure * 0.1) / 100
        probability = 1 / (1 + np.exp(-risk_score))
        return min(0.95, max(0.05, probability))
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        return 0.5

def calculate_roi(investment: float, cost_reduction: float, productivity_gain: float, employees_count: int, avg_salary: float = 5000) -> dict:
    """Calcula ROI de iniciativas de bem-estar"""
    try:
        annual_savings = cost_reduction + (productivity_gain / 100 * avg_salary * 12 * employees_count)
        roi = ((annual_savings - investment) / investment) * 100 if investment > 0 else 0
        payback_period = investment / annual_savings if annual_savings > 0 else float('inf')
        
        return {
            "roi_percentage": round(roi, 2),
            "payback_period": round(payback_period, 2),
            "annual_savings": round(annual_savings, 2),
            "net_return": round(annual_savings - investment, 2),
            "break_even_months": round(payback_period * 12, 1)
        }
    except Exception as e:
        logger.error(f"Erro no cálculo de ROI: {e}")
        return {"error": str(e)}

def get_recommendations(risk_level: str) -> list:
    """Retorna recomendações baseadas no nível de risco"""
    recommendations = {
        "BAIXO": [
            "Manter monitoramento regular das métricas",
            "Continuar programas de bem-estar existentes",
            "Coletar feedback constante dos colaboradores",
            "Manter comunicação transparente"
        ],
        "MÉDIO": [
            "Revisar carga de trabalho e distribuição de tarefas",
            "Implementar programas de mentoria e desenvolvimento",
            "Oferecer suporte psicológico e coaching",
            "Avaliar condições ergonômicas do ambiente",
            "Implementar pesquisas de clima organizacional"
        ],
        "ALTO": [
            "Intervenção imediata da liderança necessária",
            "Revisão urgente de carga horária e turnos",
            "Suporte psicológico obrigatório e acompanhamento",
            "Avaliação completa da liderança e gestão",
            "Plano de ação emergencial com metas claras",
            "Comunicação transparente com toda a equipe"
        ]
    }
    return recommendations.get(risk_level, [])

# Rotas da API
@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Endpoint raiz com informações do serviço"""
    return HealthCheckResponse(
        status="online",
        service="sst-api",
        timestamp=datetime.now().isoformat(),
        environment="production" if RENDER else "development",
        github_repo=GITHUB_REPO
    )

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check para monitoramento"""
    return HealthCheckResponse(
        status="healthy",
        service="sst-api",
        timestamp=datetime.now().isoformat(),
        environment="production" if RENDER else "development",
        github_repo=GITHUB_REPO
    )

@app.post("/predict/turnover")
async def predict_turnover_route(request: TurnoverPredictionRequest):
    """
    Prediz a probabilidade de turnover baseado em métricas de SST
    """
    try:
        probability = predict_turnover(
            request.overtime_hours,
            request.burnout_score,
            request.training_hours,
            request.tenure_years
        )
        
        risk_level = "ALTO" if probability > 0.7 else "MÉDIO" if probability > 0.4 else "BAIXO"
        
        return {
            "probability": round(probability * 100, 2),
            "risk_level": risk_level,
            "recommendations": get_recommendations(risk_level),
            "timestamp": datetime.now().isoformat(),
            "input_parameters": {
                "overtime_hours": request.overtime_hours,
                "burnout_score": request.burnout_score,
                "training_hours": request.training_hours,
                "tenure_years": request.tenure_years
            }
        }
    except Exception as e:
        logger.error(f"Erro na rota de predição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@app.post("/calculate/roi")
async def calculate_roi_route(request: ROICalculationRequest):
    """
    Calcula ROI de investimentos em bem-estar corporativo
    """
    try:
        result = calculate_roi(
            request.investment,
            request.cost_reduction,
            request.productivity_gain,
            request.employees_count
        )
        result["timestamp"] = datetime.now().isoformat()
        result["input_parameters"] = {
            "investment": request.investment,
            "cost_reduction": request.cost_reduction,
            "productivity_gain": request.productivity_gain,
            "employees_count": request.employees_count
        }
        return result
    except Exception as e:
        logger.error(f"Erro na rota de ROI: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no cálculo: {str(e)}")

@app.get("/sample/data")
async def get_sample_data():
    """Retorna dados de exemplo para demonstração do dashboard"""
    try:
        departments = ['Agência Centro', 'Agência Norte', 'Agência Sul', 'Agência Leste', 'Agência Oeste', 'Matriz']
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        data = []
        for dept in departments:
            for month in months:
                data.append({
                    'department': dept,
                    'month': month,
                    'turnover_rate': round(np.random.uniform(0.05, 0.25), 3),
                    'overtime_hours': round(np.random.uniform(30, 60), 1),
                    'burnout_score': round(np.random.uniform(40, 80), 1),
                    'productivity': round(np.random.uniform(65, 85), 1),
                    'health_costs': round(np.random.uniform(50000, 120000), 2),
                    'accidents': np.random.randint(0, 3),
                    'risk_score': round(np.random.uniform(0.3, 0.8), 3)
                })
        
        return {
            "data": data, 
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
            "description": "Dados simulados para demonstração do dashboard SST"
        }
    except Exception as e:
        logger.error(f"Erro ao gerar dados sample: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dados: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Endpoint para métricas do Prometheus"""
    return {
        "status": "metrics_endpoint",
        "message": "Métricas disponíveis para monitoramento",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
