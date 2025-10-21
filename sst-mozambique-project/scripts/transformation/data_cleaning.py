#!/usr/bin/env python3
"""
Script de limpeza e transformação de dados SST
"""

import pandas as pd
import numpy as np
import json

class SSTDataCleaning:
    def __init__(self):
        self.provinces_mozambique = [
            'Maputo', 'Gaza', 'Inhambane', 'Sofala', 'Manica',
            'Tete', 'Zambézia', 'Nampula', 'Cabo Delgado', 'Niassa'
        ]
    
    def clean_accident_data(self, raw_data):
        """Limpa e valida dados de acidentes"""
        try:
            # Validar província
            if raw_data.get('province') not in self.provinces_mozambique:
                raw_data['province'] = 'Desconhecida'
                raw_data['data_quality_score'] = 0.5
            
            # Validar datas
            if not raw_data.get('accident_date'):
                raw_data['data_quality_score'] = 0.3
            
            # Validar setor econômico
            valid_sectors = ['Construção', 'Mineração', 'Agricultura', 'Indústria', 'Serviços', 'Transporte']
            if raw_data.get('economic_sector') not in valid_sectors:
                raw_data['economic_sector'] = 'Outros'
            
            return raw_data
        except Exception as e:
            print(f"Erro na limpeza: {e}")
            return raw_data
    
    def calculate_kpis(self, data_list):
        """Calcula KPIs de SST"""
        total_accidents = len(data_list)
        fatal_accidents = sum(1 for d in data_list if d.get('fatal'))
        total_days_lost = sum(d.get('days_lost', 0) for d in data_list)
        total_injured = sum(d.get('injured_count', 0) for d in data_list)
        
        kpis = {
            'total_acidentes': total_accidents,
            'acidentes_fatais': fatal_accidents,
            'taxa_fatalidade': fatal_accidents / total_accidents if total_accidents > 0 else 0,
            'total_dias_perdidos': total_days_lost,
            'total_feridos': total_injured,
            'dias_perdidos_por_acidente': total_days_lost / total_accidents if total_accidents > 0 else 0
        }
        
        return kpis
