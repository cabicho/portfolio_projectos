import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import streamlit as st

class MulticlassModel:
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    @st.cache_resource(show_spinner="Treinando modelo multiclasse...")
    def train_model(_self, data):
        """Treina modelo de classificação multiclasse"""
        try:
            # Preparar features e target
            features = data[['valor_estimado', 'crescimento_projetado', 'roi_esperado', 'potencial_mercado']]
            target = data['classe_predita']
            
            # Treinar modelo
            _self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            _self.model.fit(features, target)
            _self.is_trained = True
            
            return _self.model
            
        except Exception as e:
            st.error(f"Erro no treinamento do modelo: {e}")
            return None
    
    def predict(self, features):
        """Faz predições com o modelo treinado"""
        if self.is_trained and self.model is not None:
            return self.model.predict(features)
        else:
            return None