# Adicionar no início do dashboard_sst.py
import json
import pickle
import sqlite3
import os
from datetime import datetime

class LocalStorage:
    """Armazenamento local para substituir Redis no free tier"""
    
    def __init__(self):
        self.data_file = "local_data.pkl"
        self.data = self._load_data()
    
    def _load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'rb') as f:
                    return pickle.load(f)
        except:
            pass
        return {}
    
    def _save_data(self):
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump(self.data, f)
        except:
            pass
    
    def set(self, key, value):
        self.data[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        self._save_data()
    
    def get(self, key, default=None):
        return self.data.get(key, {}).get('value', default)

# Usar storage local
storage = LocalStorage()