import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_ship_data(num_records=1000):
    """Gera dados fictícios de frota de navios"""
    np.random.seed(42)
    
    # Portos brasileiros principais
    ports = ['Santos', 'Rio de Janeiro', 'Paranaguá', 'Itajaí', 'Rio Grande', 
             'Salvador', 'Fortaleza', 'Manaus', 'Belém', 'Recife']
    
    # Tipos de navios
    ship_types = ['Container', 'Granelheiro', 'Petroleiro', 'Gaseiro', 'Graneleiro']
    
    # Dados dos navios
    ships_data = []
    
    for i in range(num_records):
        ship_id = f"SHIP_{i:03d}"
        ship_type = random.choice(ship_types)
        capacity = np.random.uniform(5000, 50000)  # toneladas
        speed = np.random.uniform(15, 25)  # nós
        fuel_consumption = np.random.uniform(20, 100)  # toneladas/dia
        operating_cost = np.random.uniform(5000, 20000)  # USD/dia
        
        # Dados de rota
        origin = random.choice(ports)
        destination = random.choice([p for p in ports if p != origin])
        distance = np.random.uniform(500, 3000)  # milhas náuticas
        
        # Tempos
        travel_time = distance / speed  # dias
        loading_time = np.random.uniform(1, 3)  # dias
        unloading_time = np.random.uniform(1, 3)  # dias
        total_time = travel_time + loading_time + unloading_time
        
        # Custos
        fuel_cost = fuel_consumption * travel_time * 650  # USD (650 USD/ton)
        port_cost = np.random.uniform(10000, 50000)
        total_cost = fuel_cost + port_cost + (operating_cost * total_time)
        
        # Receita
        revenue = np.random.uniform(total_cost * 1.1, total_cost * 1.5)
        profit = revenue - total_cost
        
        # Disponibilidade
        maintenance_due = np.random.randint(0, 100) < 10  # 10% precisam de manutenção
        
        ships_data.append({
            'ship_id': ship_id,
            'ship_type': ship_type,
            'capacity_ton': round(capacity, 2),
            'speed_knots': round(speed, 2),
            'fuel_consumption_td': round(fuel_consumption, 2),
            'operating_cost_usd_d': round(operating_cost, 2),
            'origin_port': origin,
            'destination_port': destination,
            'distance_nm': round(distance, 2),
            'travel_time_days': round(travel_time, 2),
            'loading_time_days': round(loading_time, 2),
            'unloading_time_days': round(unloading_time, 2),
            'total_time_days': round(total_time, 2),
            'fuel_cost_usd': round(fuel_cost, 2),
            'port_cost_usd': round(port_cost, 2),
            'total_cost_usd': round(total_cost, 2),
            'revenue_usd': round(revenue, 2),
            'profit_usd': round(profit, 2),
            'maintenance_due': maintenance_due,
            'utilization_rate': np.random.uniform(0.6, 0.95),
            'fuel_efficiency': round(profit / fuel_consumption, 2)
        })
    
    df = pd.DataFrame(ships_data)
    df.to_csv('data/ships_data.csv', index=False)
    
    # Salvar estatísticas
    stats = {
        'total_records': len(df),
        'total_profit_potential': df['profit_usd'].sum(),
        'avg_profit_per_ship': df['profit_usd'].mean(),
        'maintenance_ships': df['maintenance_due'].sum(),
        'most_profitable_type': df.groupby('ship_type')['profit_usd'].mean().idxmax(),
        'most_used_port': pd.concat([df['origin_port'], df['destination_port']]).mode()[0]
    }
    
    with open('data/dataset_stats.txt', 'w') as f:
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")
    
    print(f"✅ Gerados {len(df)} registros de dados de navios")
    print(f"📊 Estatísticas básicas:")
    print(f"   - Lucro total potencial: USD {df['profit_usd'].sum():,.2f}")
    print(f"   - Lucro médio por navio: USD {df['profit_usd'].mean():,.2f}")
    print(f"   - Custo médio: USD {df['total_cost_usd'].mean():,.2f}")
    print(f"   - Tempo médio viagem: {df['travel_time_days'].mean():.2f} dias")
    print(f"   - Navios em manutenção: {df['maintenance_due'].sum()}")
    print(f"   - Tipo mais lucrativo: {stats['most_profitable_type']}")
    
    return df

if __name__ == "__main__":
    generate_ship_data(1000)
