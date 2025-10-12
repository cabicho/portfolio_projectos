import pandas as pd
import os
from typing import List, Dict

class ExcelSharePointExtractor:
    """
    Extrator para dados de Excel e SharePoint
    """
    
    def extract_excel_files(self, directory_path: str) -> Dict[str, pd.DataFrame]:
        """Extrai dados de múltiplos arquivos Excel"""
        dataframes = {}
        
        for file in os.listdir(directory_path):
            if file.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(directory_path, file)
                try:
                    df = pd.read_excel(file_path)
                    dataframes[file] = df
                    print(f"✅ Arquivo Excel processado: {file}")
                except Exception as e:
                    print(f"❌ Erro ao processar {file}: {e}")
        
        return dataframes
    
    def extract_csv_files(self, directory_path: str) -> Dict[str, pd.DataFrame]:
        """Extrai dados de arquivos CSV"""
        dataframes = {}
        
        for file in os.listdir(directory_path):
            if file.endswith('.csv'):
                file_path = os.path.join(directory_path, file)
                try:
                    df = pd.read_csv(file_path)
                    dataframes[file] = df
                    print(f"✅ Arquivo CSV processado: {file}")
                except Exception as e:
                    print(f"❌ Erro ao processar {file}: {e}")
        
        return dataframes
    
    def consolidate_data(self, dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Consolida múltiplos dataframes"""
        consolidated_df = pd.DataFrame()
        
        for name, df in dataframes.items():
            # Adicionar coluna de origem
            df['fonte_arquivo'] = name
            consolidated_df = pd.concat([consolidated_df, df], ignore_index=True)
        
        return consolidated_df
