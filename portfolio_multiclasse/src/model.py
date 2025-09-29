import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class MulticlassModel:
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    def train_model(self, data):
        """Treina modelo de classificação multiclasse"""
        try:
            # Preparar features e target
            features = data[['valor_estimado', 'crescimento_projetado', 'roi_esperado', 'potencial_mercado']]
            target = data['classe_predita']
            
            # Treinar modelo
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(features, target)
            self.is_trained = True
            
            return self.model
            
        except Exception as e:
            print(f"Erro no treinamento do modelo: {e}")
            return None
    
    def predict(self, features):
        """Faz predições com o modelo treinado"""
        if self.is_trained and self.model is not None:
            return self.model.predict(features)
        else:
            return None
