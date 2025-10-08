#!/usr/bin/env python3

import pandas as pd
import os
import logging
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, db_url, data_path):
        self.engine = create_engine(db_url)
        self.data_path = data_path
    
    def load_processed_data(self):
        """Carrega dados processados para o data warehouse"""
        try:
            customers = pd.read_csv(f'{self.data_path}/processed/dim_customers_processed.csv')
            products = pd.read_csv(f'{self.data_path}/processed/dim_products_processed.csv')
            sales = pd.read_csv(f'{self.data_path}/processed/fact_sales_processed.csv')
            
            customers.to_sql('customers', self.engine, if_exists='replace', index=False)
            products.to_sql('products', self.engine, if_exists='replace', index=False)
            sales.to_sql('sales', self.engine, if_exists='replace', index=False)
            
            logger.info("✅ Dados carregados para o Data Warehouse")
            logger.info(f"   - Customers: {len(customers)} registros")
            logger.info(f"   - Products: {len(products)} registros")
            logger.info(f"   - Sales: {len(sales)} registros")
            
        except Exception as e:
            logger.error(f"❌ Erro no carregamento de dados: {e}")
            raise

if __name__ == "__main__":
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    data_path = os.getenv('DATA_PATH', './data')
    loader = DataLoader(db_url, data_path)
    loader.load_processed_data()
