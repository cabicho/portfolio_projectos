#!/bin/bash
# setup-render.sh
#Execute o script de setup:

#chmod +x setup-render.sh
#./setup-render.sh

echo "🚀 Preparando projeto para deploy no Render..."

# Criar estrutura de diretórios
mkdir -p api

# Criar arquivos necessários
echo "📁 Criando estrutura de arquivos..."

# Criar render.yaml (já feito acima)

# Criar api/app.py
cat > api/app.py << 'EOF'
from flask import Flask, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/kpis')
def get_kpis():
    kpis = {
        "total_revenue": 285982336,
        "eligible_stores": 1247,
        "model_accuracy": 89.2,
        "attention_stores": 84
    }
    return jsonify(kpis)

@app.route('/api/predictions')
def get_predictions():
    predictions = [
        {"week": 1, "revenue": 48500000},
        {"week": 2, "revenue": 47200000},
        {"week": 3, "revenue": 46800000},
        {"week": 4, "revenue": 47500000},
        {"week": 5, "revenue": 48000000},
        {"week": 6, "revenue": 47900000}
    ]
    return jsonify(predictions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

# Criar build_assets.py
cat > build_assets.py << 'EOF'
import os
import shutil

def build_assets():
    """Copia assets para o diretório correto no build do Render"""
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    if os.path.exists('assets/styles.css'):
        print("✅ Assets CSS encontrados")
    else:
        with open('assets/styles.css', 'w') as f:
            f.write("/* CSS do Dashboard Rossmann */\n")
        print("📁 CSS básico criado")
    
    print("✅ Build de assets concluído")

if __name__ == '__main__':
    build_assets()
EOF

# Criar worker.py
cat > worker.py << 'EOF'
import time
import os

def main():
    print("🚀 Worker Rossmann iniciado")
    while True:
        print("🤖 Worker rodando...", time.ctime())
        time.sleep(60)

if __name__ == '__main__':
    main()
EOF

# Criar runtime.txt
echo "python-3.9.0" > runtime.txt

# Atualizar app.py para produção
cat > app.py << 'EOF'
"""
Dashboard Executivo - Rossmann - Versão Render
"""

import os
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output

# Configurações Render
DEBUG = os.getenv('DASH_DEBUG_MODE', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', 8050))
RENDER = os.getenv('RENDER', 'false').lower() == 'true'

# Importações dos componentes
try:
    from components.kpi_cards import initialize_kpi_cards, register_kpi_callbacks
    from components.trend_chart import create_trend_chart, register_trend_callbacks
    from components.heat_map import create_heat_map, register_heatmap_callbacks
    from components.alerts_panel import create_alerts_panel, register_alerts_callbacks
    from components.comparison_table import create_comparison_table, register_comparison_callbacks
    from components.filters import create_filters_component
except ImportError as e:
    print(f"⚠️ Erro ao importar componentes: {e}")
    # Fallbacks
    def initialize_kpi_cards(app): return html.Div("Carregando...")
    def create_trend_chart(): return html.Div("Carregando...")
    def create_heat_map(): return html.Div("Carregando...")
    def create_alerts_panel(): return html.Div("Carregando...")
    def create_comparison_table(): return html.Div("Carregando...")
    def create_filters_component(): return html.Div("Carregando...")
    def register_kpi_callbacks(app): pass
    def register_trend_callbacks(app): pass
    def register_heatmap_callbacks(app): pass
    def register_alerts_callbacks(app): pass
    def register_comparison_callbacks(app): pass

# Configuração da aplicação
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

app.title = "📊 Rossmann - Dashboard Executivo"

# Layout principal
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📊 Dashboard Executivo - Rossmann", className="text-center mb-2"),
            html.P("Previsão de vendas para as próximas 6 semanas", className="text-center text-muted mb-4"),
            html.Div([
                dbc.Badge("Render", color="info", className="me-2"),
                dbc.Badge("Produção", color="success")
            ], className="text-center")
        ], width=12)
    ], className="dashboard-header"),
    
    create_filters_component(),
    initialize_kpi_cards(app),
    
    dbc.Row([
        dbc.Col(create_trend_chart(), width=6, className="mb-4"),
        dbc.Col(create_heat_map(), width=6, className="mb-4"),
    ]),
    
    dbc.Row([
        dbc.Col(create_alerts_panel(), width=6, className="mb-4"),
        dbc.Col(create_comparison_table(), width=6, className="mb-4"),
    ]),
    
    dcc.Interval(id='interval-component', interval=60000, n_intervals=0),
    dcc.Store(id='filter-store')
], fluid=True)

# Callbacks
@app.callback(
    Output("last-update", "children"),
    Input("interval-component", "n_intervals")
)
def update_time(n):
    from datetime import datetime
    return f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"

# Registrar callbacks
_callbacks_registered = False
if not _callbacks_registered:
    register_kpi_callbacks(app)
    register_trend_callbacks(app)
    register_heatmap_callbacks(app)
    register_alerts_callbacks(app)
    register_comparison_callbacks(app)
    _callbacks_registered = True

server = app.server

if __name__ == '__main__':
    print(f"🚀 Iniciando no Render - Porta: {PORT}")
    app.run_server(debug=DEBUG, host='0.0.0.0', port=PORT)
EOF

echo "✅ Setup para Render concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. git add ."
echo "2. git commit -m 'Preparar para deploy no Render'"
echo "3. git push"
echo "4. Conectar repositório no Render.com"
echo "5. Deploy automático!"