"""
Dashboard Executivo - Rossmann Sales Prediction
Versão Corrigida - Callbacks Únicos
"""

import os
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output

# Configurações Docker
DEBUG = os.getenv('DASH_DEBUG_MODE', 'False').lower() == 'true'
HOST = '0.0.0.0'
PORT = int(os.getenv('PORT', 8050))

# Importações dos componentes
try:
    from components.kpi_cards import initialize_kpi_cards, register_kpi_callbacks
    from components.trend_chart import create_trend_chart, register_trend_callbacks
    from components.heat_map import create_heat_map, register_heatmap_callbacks
    from components.alerts_panel import create_alerts_panel, register_alerts_callbacks
    from components.comparison_table import create_comparison_table, register_comparison_callbacks
    from components.filters import create_filters_component
except ImportError as e:
    print(f"Erro ao importar componentes: {e}")
    # Fallback para desenvolvimento
    def initialize_kpi_cards(app): return html.Div("Loading...")
    def create_trend_chart(): return html.Div("Loading...")
    def create_heat_map(): return html.Div("Loading...")
    def create_alerts_panel(): return html.Div("Loading...")
    def create_comparison_table(): return html.Div("Loading...")
    def create_filters_component(): return html.Div("Loading...")
    # Funções vazias para callbacks
    def register_kpi_callbacks(app): pass
    def register_trend_callbacks(app): pass
    def register_heatmap_callbacks(app): pass
    def register_alerts_callbacks(app): pass
    def register_comparison_callbacks(app): pass

# Configuração da aplicação
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

app.title = "📊 Rossmann - Dashboard Executivo"

# Layout principal
app.layout = dbc.Container([
    
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("📊 Dashboard Executivo - Rossmann", 
                   className="text-center mb-2"),
            html.P("Previsão de vendas para as próximas 6 semanas", 
                  className="text-center text-muted mb-4"),
            html.Div([
                dbc.Badge("Docker", color="primary", className="me-2"),
                dbc.Badge("Produção" if not DEBUG else "Desenvolvimento", 
                         color="success" if not DEBUG else "warning")
            ], className="text-center")
        ], width=12)
    ], className="dashboard-header"),
    
    # Componente de Filtros
    create_filters_component(),
    
    # KPI Cards
    initialize_kpi_cards(app),
    
    # Primeira linha de gráficos
    dbc.Row([
        dbc.Col(create_trend_chart(), width=6, className="mb-4"),
        dbc.Col(create_heat_map(), width=6, className="mb-4"),
    ]),
    
    # Segunda linha de componentes
    dbc.Row([
        dbc.Col(create_alerts_panel(), width=6, className="mb-4"),
        dbc.Col(create_comparison_table(), width=6, className="mb-4"),
    ]),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                "Desenvolvido com ❤️ para ",
                html.Strong("Rossmann Sales Prediction"),
                " | ",
                html.Small("Última atualização: ", id="last-update"),
                html.Small("", className="text-muted")
            ], className="text-center text-muted")
        ])
    ]),
    
    # Componentes ocultos para atualização
    dcc.Interval(id='interval-component', interval=60000, n_intervals=0),
    dcc.Store(id='filter-store'),
    dcc.Store(id='kpi-data-store')
    
], fluid=True, className="main-container")

# Callback simples para evitar duplicação
@app.callback(
    Output("last-update", "children"),
    Input("interval-component", "n_intervals")
)
def update_last_update(n):
    from datetime import datetime
    return f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"

# Variável para controlar se os callbacks já foram registrados
_callbacks_registered = False

def register_all_callbacks():
    """Registra todos os callbacks da aplicação APENAS UMA VEZ"""
    global _callbacks_registered
    
    if not _callbacks_registered:
        try:
            register_kpi_callbacks(app)
            register_trend_callbacks(app)
            register_heatmap_callbacks(app)
            register_alerts_callbacks(app)
            register_comparison_callbacks(app)
            _callbacks_registered = True
            print("✅ Todos os callbacks registrados com sucesso")
        except Exception as e:
            print(f"⚠️ Erro ao registrar callbacks: {e}")

# Registra callbacks APENAS quando o app inicia
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true' or not DEBUG:
    register_all_callbacks()

# Servidor para produção
server = app.server

if __name__ == '__main__':
    print(f"🚀 Iniciando Dashboard Rossmann")
    print(f"🔧 Debug: {DEBUG}")
    print(f"🌐 Host: {HOST}")
    print(f"📡 Porta: {PORT}")
    
    app.run_server(
        debug=DEBUG,
        host=HOST,
        port=PORT,
        dev_tools_ui=DEBUG,
        dev_tools_hot_reload=DEBUG
    )
