from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
from datetime import datetime
import logging

# Configuração
RENDER = os.getenv('RENDER', False)

app = FastAPI(
    title="SST Prediction API - Cabicho Portfolio",
    description="API para predição de métricas de Saúde e Segurança no Trabalho",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
async def root():
    return {
        "message": "SST Prediction API - Render Free Tier", 
        "status": "online", 
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sst-api"}

@app.post("/predict/turnover")
async def predict_turnover_route(request: TurnoverPredictionRequest):
    try:
        risk_score = (request.overtime_hours * 0.3 + 
                     request.burnout_score * 0.4 - 
                     request.training_hours * 0.2 - 
                     request.tenure_years * 0.1) / 100
        probability = 1 / (1 + np.exp(-risk_score))
        probability = min(0.95, max(0.05, probability))
        
        risk_level = "ALTO" if probability > 0.7 else "MÉDIO" if probability > 0.4 else "BAIXO"
        
        return {
            "probability": round(probability * 100, 2),
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@app.post("/calculate/roi")
async def calculate_roi_route(request: ROICalculationRequest):
    try:
        avg_salary = 5000
        annual_savings = request.cost_reduction + (request.productivity_gain / 100 * avg_salary * 12 * request.employees_count)
        roi = ((annual_savings - request.investment) / request.investment) * 100 if request.investment > 0 else 0
        payback_period = request.investment / annual_savings if annual_savings > 0 else float('inf')
        
        return {
            "roi_percentage": round(roi, 2),
            "payback_period": round(payback_period, 2),
            "annual_savings": round(annual_savings, 2),
            "net_return": round(annual_savings - request.investment, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no cálculo: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
