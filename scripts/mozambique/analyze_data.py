# scripts/mozambique/analyze_data.py
#!/usr/bin/env python3
import pandas as pd
import plotly.express as px
import json
import os

print("🔍 Iniciando análise de dados...")

# Carregar dados
df_empresas = pd.read_csv('data/mozambique/raw/empresas.csv')

# Análise básica
resultados = {
    'total_empresas': len(df_empresas),
    'roi_medio': float(df_empresas['roi'].mean()),
    'burnout_medio': float(df_empresas['burnout_medio'].mean()),
    'produtividade_media': float(df_empresas['produtividade'].mean()),
    'acidentes_medio': float(df_empresas['acidentes_ano'].mean()),
    'setor_mais_rentavel': df_empresas.groupby('setor')['roi'].mean().idxmax(),
    'provincia_mais_produtiva': df_empresas.groupby('provincia')['produtividade'].mean().idxmax()
}

# Dashboard simples
fig = px.box(df_empresas, x='setor', y='roi', title='ROI por Setor')
fig.write_html('data/mozambique/reports/dashboard_setorial.html')

fig2 = px.scatter(df_empresas, x='burnout_medio', y='produtividade', 
                 color='setor', title='Burnout vs Produtividade')
fig2.write_html('data/mozambique/reports/correlacao_burnout.html')

# Salvar resultados
with open('data/mozambique/reports/resultados.json', 'w') as f:
    json.dump(resultados, f, indent=2)

print("✅ Análise concluída!")
print(f"📊 ROI médio: {resultados['roi_medio']:.1f}%")
print(f"🔥 Burnout médio: {resultados['burnout_medio']:.2f}/7")
print(f"⚡ Produtividade média: {resultados['produtividade_media']:.1f}")