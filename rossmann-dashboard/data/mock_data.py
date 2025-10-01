"""
Gerador de dados mockados para desenvolvimento
"""

import random
from datetime import datetime, timedelta

def generate_mock_kpi_data():
    """Gera dados mockados para os KPIs"""
    return {
        "total_revenue": {
            "current": 285982336,
            "previous": 279500000,
            "change_percent": 2.32,
            "trend": "up"
        },
        "eligible_stores": {
            "current": 1247,
            "previous": 1186,
            "change_percent": 5.14,
            "trend": "up",
            "total_stores": 1978
        },
        "model_accuracy": {
            "current": 89.2,
            "previous": 87.5,
            "change_percent": 1.94,
            "trend": "up"
        },
        "attention_stores": {
            "current": 84,
            "previous": 96,
            "change_percent": -12.50,
            "trend": "down"
        }
    }

def generate_trend_data():
    """Gera dados para o gráfico de tendência"""
    weeks = [f"Semana {i}" for i in range(1, 7)]
    
    base_forecast = 48500000
    base_historical = 46500000
    
    forecast_2024 = [
        base_forecast * (1 + random.uniform(-0.03, 0.02)) 
        for _ in range(6)
    ]
    
    historical_2023 = [
        base_historical * (1 + random.uniform(-0.02, 0.01))
        for _ in range(6)
    ]
    
    return {
        'weeks': weeks,
        'forecast_2024': forecast_2024,
        'historical_2023': historical_2023
    }

def generate_heatmap_data():
    """Gera dados para o mapa de calor"""
    
    # GeoJSON simplificado para regiões do Brasil
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Sudeste"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-50, -25], [-40, -25], [-40, -15], [-50, -15], [-50, -25]]]
                }
            },
            {
                "type": "Feature", 
                "properties": {"name": "Sul"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-60, -35], [-50, -35], [-50, -25], [-60, -25], [-60, -35]]]
                }
            }
        ]
    }
    
    return {
        'geojson': geojson,
        'locations': ['Sudeste', 'Sul'],
        'z_values': [68.9, 59.4],
        'region_names': ['Sudeste', 'Sul']
    }

def generate_alerts_data():
    """Gera dados de alertas"""
    return [
        {
            "id": 1,
            "type": "critical",
            "store": "Loja #2847 - SP",
            "message": "Queda de 22% na previsão vs histórico",
            "time": "2 horas atrás",
            "action": "Revisar estratégia local"
        },
        {
            "id": 2, 
            "type": "warning",
            "store": "Loja #1562 - RJ",
            "message": "Performance 12% abaixo da média regional",
            "time": "5 horas atrás", 
            "action": "Monitorar próxima semana"
        },
        {
            "id": 3,
            "type": "info",
            "store": "Loja #0891 - RS", 
            "message": "Oportunidade: 8% acima da previsão",
            "time": "1 dia atrás",
            "action": "Investigar melhores práticas"
        }
    ]

def generate_comparison_data():
    """Gera dados para tabela comparativa"""
    stores = []
    regions = ['SP', 'RJ', 'RS', 'MG', 'BA', 'CE']
    
    for i in range(20):
        store_id = f"#{random.randint(1000, 5000):04d}"
        region = random.choice(regions)
        vs_avg = random.uniform(-15, 25)
        revenue = random.randint(2000000, 5000000)
        
        stores.append({
            "store": store_id,
            "region": region,
            "vs_avg": vs_avg,
            "vs_avg_display": f"{vs_avg:+.1f}%",
            "revenue": f"R$ {revenue/1000000:.1f}M"
        })
    
    return stores
