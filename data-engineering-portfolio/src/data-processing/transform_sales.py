#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self, raw_path, processed_path):
        self.raw_path = raw_path
        self.processed_path = processed_path
        
    def clean_customer_data(self, df):
        """Limpa e transforma dados de clientes"""
        df_clean = df.copy()
        
        # Padronizar segmentos
        segment_mapping = {
            'Consumer': 'Consumer',
            'Corporate': 'Corporate', 
            'Home Office': 'Home Office'
        }
        df_clean['segment'] = df_clean['segment'].map(segment_mapping)
        
        # Adicionar coluna de país (exemplo)
        df_clean['country'] = 'USA'
        
        logger.info(f"✅ Dados de clientes transformados: {len(df_clean)} registros")
        return df_clean
    
    def clean_product_data(self, df):
        """Limpa e transforma dados de produtos"""
        df_clean = df.copy()
        
        # Calcular margem de lucro (exemplo)
        df_clean['cost'] = df_clean['price'] * 0.6  # 40% margem
        df_clean['profit_margin'] = (df_clean['price'] - df_clean['cost']) / df_clean['price']
        
        logger.info(f"✅ Dados de produtos transformados: {len(df_clean)} registros")
        return df_clean
    
    def clean_sales_data(self, df):
        """Limpa e transforma dados de vendas"""
        df_clean = df.copy()
        
        # Calcular valor total
        df_clean['total_amount'] = df_clean['quantity'] * df_clean['amount']
        
        # Extrair componentes da data
        df_clean['sale_date'] = pd.to_datetime(df_clean['sale_date'])
        df_clean['sale_year'] = df_clean['sale_date'].dt.year
        df_clean['sale_month'] = df_clean['sale_date'].dt.month
        df_clean['sale_quarter'] = df_clean['sale_date'].dt.quarter
        
        # Remover vendas com valores negativos (exemplo de validação)
        initial_count = len(df_clean)
        df_clean = df_clean[df_clean['total_amount'] > 0]
        final_count = len(df_clean)
        
        if initial_count != final_count:
            logger.warning(f"⚠️  {initial_count - final_count} vendas com valores inválidos removidas")
        
        logger.info(f"✅ Dados de vendas transformados: {len(df_clean)} registros")
        return df_clean
    
    def process_all_data(self):
        """Processa todos os dados"""
        try:
            # Carregar dados brutos
            customers = pd.read_csv(f'{self.raw_path}/raw/dim_customers_raw.csv')
            products = pd.read_csv(f'{self.raw_path}/raw/dim_products_raw.csv')
            sales = pd.read_csv(f'{self.raw_path}/raw/fact_sales_raw.csv')
            
            # Aplicar transformações
            customers_clean = self.clean_customer_data(customers)
            products_clean = self.clean_product_data(products)
            sales_clean = self.clean_sales_data(sales)
            
            # Salvar dados processados
            customers_clean.to_csv(f'{self.processed_path}/processed/dim_customers_processed.csv', index=False)
            products_clean.to_csv(f'{self.processed_path}/processed/dim_products_processed.csv', index=False)
            sales_clean.to_csv(f'{self.processed_path}/processed/fact_sales_processed.csv', index=False)
            
            logger.info("✅ Todos os dados foram transformados com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro na transformação de dados: {e}")
            raise

if __name__ == "__main__":
    data_path = os.getenv('DATA_PATH', './data')
    transformer = DataTransformer(data_path, data_path)
    transformer.process_all_data()
