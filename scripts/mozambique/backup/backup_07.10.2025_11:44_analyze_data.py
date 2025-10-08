#!/usr/bin/env python3
import pandas as pd
import plotly.express as px
import json

print("🔍 Analisando dados...")

# Carregar dados
df = pd.read_csv('data/mozambique/raw/empresas.csv')

# Análise básica
resultados = {
    'total_empresas': len(df),
    'roi_medio': float(df['roi'].mean()),
    'burnout_medio': float(df['burnout'].mean()),
    'setor_mais_rentavel': df.groupby('setor')['roi'].mean().idxmax(),
    'provincia_mais_produtiva': df.groupby('provincia')['produtividade'].mean().idxmax()
}

# Dashboard simples
fig = px.bar(df.groupby('setor')['roi'].mean().reset_index(), 
             x='setor', y='roi', title='ROI por Setor')
fig.write_html('data/mozambique/reports/dashboard.html')

# Salvar resultados
with open('data/mozambique/reports/resultados.json', 'w') as f:
    json.dump(resultados, f, indent=2)

print("✅ Análise concluída!")
print(f"📊 ROI médio: {resultados['roi_medio']:.1f}%")
print(f"🔥 Burnout médio: {resultados['burnout_medio']:.2f}/7")
