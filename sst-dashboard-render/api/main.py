from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SST Prediction API", version="1.0.0")

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

# Funções de predição
def predict_turnover(overtime: float, burnout: float, training: float, tenure: float) -> float:
    """Modelo simplificado de previsão de turnover"""
    try:
        risk_score = (overtime * 0.3 + burnout * 0.4 - training * 0.2 - tenure * 0.1) / 100
        probability = 1 / (1 + np.exp(-risk_score))
        return min(0.95, max(0.05, probability))
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        return 0.5

def calculate_roi(investment: float, cost_reduction: float, productivity_gain: float, avg_salary: float = 5000) -> dict:
    """Calcula ROI de iniciativas de bem-estar"""
    try:
        annual_savings = cost_reduction + (productivity_gain / 100 * avg_salary * 12)
        roi = ((annual_savings - investment) / investment) * 100 if investment > 0 else 0
        payback_period = investment / annual_savings if annual_savings > 0 else float('inf')
        
        return {
            "roi_percentage": round(roi, 2),
            "payback_period": round(payback_period, 2),
            "annual_savings": round(annual_savings, 2),
            "net_return": round(annual_savings - investment, 2)
        }
    except Exception as e:
        logger.error(f"Erro no cálculo de ROI: {e}")
        return {"error": str(e)}

# Rotas da API
@app.get("/")
async def root():
    return {
        "message": "SST Prediction API", 
        "status": "online", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sst-api"}

@app.post("/predict/turnover")
async def predict_turnover_route(request: TurnoverPredictionRequest):
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
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na rota de predição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@app.post("/calculate/roi")
async def calculate_roi_route(request: ROICalculationRequest):
    try:
        result = calculate_roi(
            request.investment,
            request.cost_reduction,
            request.productivity_gain
        )
        result["timestamp"] = datetime.now().isoformat()
        return result
    except Exception as e:
        logger.error(f"Erro na rota de ROI: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no cálculo: {str(e)}")

@app.get("/sample/data")
async def get_sample_data():
    """Retorna dados de exemplo para o dashboard"""
    try:
        departments = ['Agência Centro', 'Agência Norte', 'Agência Sul', 'Agência Leste', 'Agência Oeste']
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
        
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
                    'accidents': np.random.randint(0, 3)
                })
        
        return {
            "data": data, 
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao gerar dados sample: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dados: {str(e)}")

def get_recommendations(risk_level: str) -> list:
    """Retorna recomendações baseadas no nível de risco"""
    recommendations = {
        "BAIXO": [
            "Manter monitoramento regular",
            "Continuar programas de bem-estar existentes",
            "Coletar feedback dos colaboradores"
        ],
        "MÉDIO": [
            "Revisar carga de trabalho",
            "Implementar programas de mentoria",
            "Oferecer suporte psicológico",
            "Avaliar condições ergonômicas"
        ],
        "ALTO": [
            "Intervenção imediata necessária",
            "Revisão urgente de carga horária",
            "Suporte psicológico obrigatório",
            "Avaliação de liderança",
            "Plano de ação emergencial"
        ]
    }
    return recommendations.get(risk_level, [])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
