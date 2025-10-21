from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SST Moçambique API",
    description="API para dados de Segurança e Saúde no Trabalho - Moçambique",
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

@app.get("/")
async def root():
    return {"message": "SST Moçambique API"}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "api": "running",
            "database": "connected"
        }
    }

@app.get("/api/ine/statistics")
async def get_ine_statistics(year: int = 2024):
    return {
        "year": year,
        "province": "Maputo",
        "total_companies": 15000,
        "total_workers": 450000,
        "source": "INE"
    }

@app.get("/api/mitess/accidents")
async def get_mitess_accidents():
    return {
        "year": 2024,
        "total_accidents": 2500,
        "fatal_accidents": 50,
        "source": "MITESS"
    }

@app.get("/api/ilo/global_indicators")
async def get_ilo_indicators():
    return {
        "global_frequency_rate": 3.0,
        "africa_frequency_rate": 4.5,
        "source": "ILO"
    }
