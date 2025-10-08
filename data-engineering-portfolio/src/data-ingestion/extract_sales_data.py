#!/usr/bin/env python3

import pandas as pd
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self, data_path):
        self.data_path = data_path
        
    def generate_sample_data(self):
        """Gera dados de exemplo para demonstração"""
        
        # Dados de clientes
        customers = pd.DataFrame({
            'customer_id': range(1, 101),
            'customer_name': [f'Customer_{i}' for i in range(1, 101)],
            'segment': ['Corporate', 'Consumer', 'Home Office'] * 33 + ['Corporate'],
            'region': ['North', 'South', 'East', 'West'] * 25,
            'registration_date': pd.date_range('2020-01-01', periods=100, freq='D')
        })
        
        # Dados de produtos
        products = pd.DataFrame({
            'product_id': range(1, 51),
            'product_name': [f'Product_{i}' for i in range(1, 51)],
            'category': ['Electronics', 'Furniture', 'Office Supplies'] * 16 + ['Electronics', 'Furniture'],
            'sub_category': ['Phones', 'Chairs', 'Binders'] * 16 + ['Phones', 'Chairs'],
            'price': [100 + i * 10 for i in range(50)]
        })
        
        # Dados de vendas
        sales = pd.DataFrame({
            'sale_id': range(1, 1001),
            'customer_id': [i % 100 + 1 for i in range(1000)],
            'product_id': [i % 50 + 1 for i in range(1000)],
            'sale_date': pd.date_range('2023-01-01', periods=1000, freq='H'),
            'quantity': [1, 2, 3, 1, 2] * 200,
            'amount': [100, 200, 150, 300, 250] * 200
        })
        
        return customers, products, sales
    
    def save_raw_data(self):
        """Salva dados brutos"""
        try:
            customers, products, sales = self.generate_sample_data()
            
            # Salvar como CSV
            customers.to_csv(f'{self.data_path}/raw/dim_customers_raw.csv', index=False)
            products.to_csv(f'{self.data_path}/raw/dim_products_raw.csv', index=False)
            sales.to_csv(f'{self.data_path}/raw/fact_sales_raw.csv', index=False)
            
            logger.info("✅ Dados brutos gerados e salvos com sucesso!")
            logger.info(f"   - Clientes: {len(customers)} registros")
            logger.info(f"   - Produtos: {len(products)} registros")
            logger.info(f"   - Vendas: {len(sales)} registros")
            
        except Exception as e:
            logger.error(f"❌ Erro na extração de dados: {e}")
            raise

if __name__ == "__main__":
    data_path = os.getenv('DATA_PATH', './data')
    extractor = DataExtractor(data_path)
    extractor.save_raw_data()
