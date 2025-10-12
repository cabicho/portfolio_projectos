import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import joblib

class HealthPredictiveAnalytics:
    """
    Machine Learning para análise preditiva em saúde ocupacional
    """
    
    def __init__(self):
        self.models = {}
    
    def predict_risk_evolution(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """Prever evolução dos scores de risco"""
        # Preparar dados para time series
        df = historical_data.copy()
        df['ano_mes'] = pd.to_datetime(df['ano'].astype(str) + '-01')
        df = df.sort_values('ano_mes')
        
        # Criar features para previsão
        for i in range(1, 3):
            df[f'score_lag_{i}'] = df['score_risco'].shift(i)
        
        df = df.dropna()
        
        if len(df) < 5:
            print("⚠️ Dados insuficientes para previsão")
            return df
        
        # Treinar modelo
        features = [col for col in df.columns if col.startswith('score_lag_')]
        X = df[features]
        y = df['score_risco']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Fazer previsões
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        
        print(f"✅ Modelo de previsão treinado - MAE: {mae:.2f}")
        
        # Prever próximo período
        last_data = df[features].iloc[-1:].values
        next_prediction = model.predict(last_data)[0]
        
        df.loc[len(df)] = {
            'provincia': 'Previsão',
            'score_risco': next_prediction,
            'nivel_risco': 'Alto' if next_prediction > 45 else 'Médio' if next_prediction > 35 else 'Baixo',
            'ano': df['ano'].max() + 1,
            'tipo': 'PREVISTO'
        }
        
        self.models['risk_predictor'] = model
        return df
    
    def cluster_provinces(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrupar províncias por similaridade de risco"""
        features = ['score_risco', 'populacao_exposta']
        
        if len(df) < 3:
            print("⚠️ Dados insuficientes para clustering")
            df['cluster'] = 0
            return df
        
        # Normalizar features
        X = df[features]
        X_normalized = (X - X.mean()) / X.std()
        
        # Aplicar K-means
        kmeans = KMeans(n_clusters=min(3, len(df)), random_state=42)
        df['cluster'] = kmeans.fit_predict(X_normalized)
        
        # Nomear clusters
        cluster_names = {
            0: 'Baixo Risco-Baixa População',
            1: 'Médio Risco-Média População', 
            2: 'Alto Risco-Alta População'
        }
        
        df['cluster_nome'] = df['cluster'].map(cluster_names)
        print("✅ Clustering de províncias concluído")
        
        return df
    
    def anomaly_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detectar anomalias nos dados"""
        from sklearn.ensemble import IsolationForest
        
        features = ['score_risco', 'populacao_exposta']
        X = df[features]
        
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        df['anomalia'] = iso_forest.fit_predict(X)
        df['anomalia'] = df['anomalia'].map({1: 'Normal', -1: 'Anomalia'})
        
        anomalies = df[df['anomalia'] == 'Anomalia']
        print(f"✅ Detecção de anomalias: {len(anomalies)} casos identificados")
        
        return df
    
    def save_models(self, directory: str):
        """Salvar modelos treinados"""
        for name, model in self.models.items():
            joblib.dump(model, f"{directory}/{name}.joblib")
            print(f"✅ Modelo {name} salvo")
