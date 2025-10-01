import os
import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configurações para Render
RENDER = os.getenv('RENDER', False)
PORT = int(os.getenv('GRADIO_SERVER_PORT', 7860))
GITHUB_REPO = os.getenv('GITHUB_REPO', 'https://github.com/cabicho/portfolio_projectos/tree/sst-dashboard/sst-dashboard-render')

def generate_sample_data():
    """Gera dados simulados para demonstração"""
    np.random.seed(42)
    
    departments = ['Agência Centro', 'Agência Norte', 'Agência Sul', 'Agência Leste', 'Agência Oeste', 'Matriz']
    months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    data = []
    for dept in departments:
        for i, month in enumerate(months):
            base_risk = np.random.normal(0.6, 0.2)
            data.append({
                'department': dept,
                'month': month,
                'month_num': i + 1,
                'turnover_rate': round(np.random.uniform(0.05, 0.25), 3),
                'overtime_hours': round(np.random.uniform(30, 60), 1),
                'burnout_score': round(np.random.uniform(40, 80), 1),
                'productivity': round(np.random.uniform(65, 85), 1),
                'health_costs': round(np.random.uniform(50000, 120000), 2),
                'accidents': np.random.randint(0, 3),
                'risk_score': round(np.random.uniform(0.3, 0.8), 3),
                'wellbeing_investment': round(np.random.uniform(20000, 80000), 2),
                'training_hours': np.random.randint(10, 40)
            })
    
    return pd.DataFrame(data)

def predict_turnover(overtime, burnout, training, tenure):
    """Modelo preditivo de turnover"""
    risk_score = (overtime * 0.3 + burnout * 0.4 - training * 0.2 - tenure * 0.1) / 100
    probability = 1 / (1 + np.exp(-risk_score))
    probability = min(0.95, max(0.05, probability))
    return probability

def calculate_roi(investment, cost_reduction, productivity_gain, employees, avg_salary=5000):
    """Calcula ROI de iniciativas de bem-estar"""
    annual_savings = cost_reduction + (productivity_gain / 100 * avg_salary * 12 * employees)
    roi = ((annual_savings - investment) / investment) * 100 if investment > 0 else 0
    payback = investment / annual_savings if annual_savings > 0 else float('inf')
    return roi, payback, annual_savings

def create_dashboard():
    """Cria o dashboard Gradio"""
    df = generate_sample_data()
    
    with gr.Blocks(theme=gr.themes.Soft(), title="Dashboard SST - Cabicho Portfolio") as dashboard:
        
        gr.Markdown(
            f"""
            # 📊 Dashboard SST & Performance Financeira
            **Portfolio Projecto | [Repositório GitHub]({GITHUB_REPO})**
            
            *Sistema de análise preditiva para Saúde e Segurança no Trabalho com impacto financeiro*
            """
        )
        
        with gr.Tabs() as tabs:
            with gr.TabItem("📈 Visão Geral"):
                with gr.Row():
                    dept_filter = gr.Dropdown(
                        choices=["Todos"] + list(df['department'].unique()),
                        value="Todos",
                        label="🔍 Filtrar por Departamento"
                    )
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 Métricas Principais")
                        
                        # Métricas em tempo real
                        avg_turnover = df['turnover_rate'].mean() * 100
                        avg_productivity = df['productivity'].mean()
                        total_health_costs = df['health_costs'].sum() / 1000000
                        total_accidents = df['accidents'].sum()
                        total_investment = df['wellbeing_investment'].sum() / 1000000
                        
                        gr.Markdown(f"""
                        **📈 Taxa Média de Turnover:** `{avg_turnover:.1f}%`
                        
                        **⚡ Produtividade Média:** `{avg_productivity:.1f}%`
                        
                        **🏥 Custos com Saúde:** `R$ {total_health_costs:.2f} Mi`
                        
                        **🚨 Acidentes Totais:** `{total_accidents}`
                        
                        **💰 Investimento em Bem-estar:** `R$ {total_investment:.2f} Mi`
                        """)
                    
                    with gr.Column(scale=2):
                        # Gráfico de turnover por departamento
                        fig_turnover = px.line(
                            df, 
                            x='month', 
                            y='turnover_rate',
                            color='department',
                            title="📊 Evolução da Taxa de Turnover por Departamento",
                            labels={'turnover_rate': 'Taxa de Turnover', 'month': 'Mês'}
                        )
                        gr.Plot(fig_turnover, label="Evolução do Turnover")
                
                with gr.Row():
                    with gr.Column():
                        # Mapa de calor de riscos
                        pivot_data = df.pivot_table(
                            values=['turnover_rate', 'burnout_score', 'accidents'], 
                            index='department', 
                            aggfunc='mean'
                        )
                        
                        fig_heatmap = px.imshow(
                            pivot_data.T,
                            title="🎯 Mapa de Calor - Métricas de Risco por Departamento",
                            color_continuous_scale="RdYlGn_r",
                            aspect="auto"
                        )
                        gr.Plot(fig_heatmap, label="Mapa de Calor")
                    
                    with gr.Column():
                        # Correlação burnout vs produtividade
                        fig_scatter = px.scatter(
                            df,
                            x='burnout_score',
                            y='productivity',
                            color='department',
                            title="📈 Relação: Burnout vs Produtividade",
                            trendline="lowess",
                            labels={'burnout_score': 'Escore de Burnout', 'productivity': 'Produtividade (%)'}
                        )
                        gr.Plot(fig_scatter, label="Relação Burnout-Produtividade")
            
            with gr.TabItem("🔮 Previsões"):
                gr.Markdown("### 🤖 Modelo Preditivo de Turnover")
                
                with gr.Row():
                    with gr.Column():
                        overtime_input = gr.Slider(10, 80, value=45, label="🕒 Horas Extras/Mês")
                        burnout_input = gr.Slider(20, 100, value=65, label="😰 Escore de Burnout")
                        training_input = gr.Slider(0, 40, value=20, label="📚 Horas de Treinamento/Mês")
                        tenure_input = gr.Slider(0, 20, value=5, label="⏳ Tempo na Empresa (anos)")
                    
                    with gr.Column():
                        prediction_output = gr.Markdown()
                        risk_gauge = gr.Plot()
                
                def update_prediction(overtime, burnout, training, tenure):
                    probability = predict_turnover(overtime, burnout, training, tenure)
                    
                    # Criar gauge plot
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = probability * 100,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "🎯 Probabilidade de Turnover"},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 30], 'color': "lightgreen"},
                                {'range': [30, 70], 'color': "yellow"},
                                {'range': [70, 100], 'color': "red"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    
                    risk_level = "ALTO" if probability > 0.7 else "MÉDIO" if probability > 0.4 else "BAIXO"
                    risk_color = "red" if risk_level == "ALTO" else "orange" if risk_level == "MÉDIO" else "green"
                    
                    recommendations = {
                        "BAIXO": [
                            "✅ Manter monitoramento regular",
                            "✅ Continuar programas de bem-estar",
                            "✅ Coletar feedback dos colaboradores"
                        ],
                        "MÉDIO": [
                            "⚠️ Revisar carga de trabalho",
                            "⚠️ Implementar programas de mentoria", 
                            "⚠️ Oferecer suporte psicológico",
                            "⚠️ Avaliar condições ergonômicas"
                        ],
                        "ALTO": [
                            "🚨 Intervenção imediata necessária",
                            "🚨 Revisão urgente de carga horária",
                            "🚨 Suporte psicológico obrigatório",
                            "🚨 Avaliação de liderança",
                            "🚨 Plano de ação emergencial"
                        ]
                    }
                    
                    rec_list = "\n".join([f"- {rec}" for rec in recommendations.get(risk_level, [])])
                    
                    return (
                        f"""
                        ### 📊 Resultado da Previsão
                        
                        **📈 Probabilidade de Turnover:** `{probability*100:.1f}%`
                        
                        **🎯 Nível de Risco:** <span style='color:{risk_color}; font-weight:bold'>{risk_level}</span>
                        
                        **💡 Recomendações:**
                        {rec_list}
                        """,
                        fig_gauge
                    )
                
                inputs = [overtime_input, burnout_input, training_input, tenure_input]
                for inp in inputs:
                    inp.change(update_prediction, inputs=inputs, outputs=[prediction_output, risk_gauge])
                
                # Valor inicial
                initial_pred = update_prediction(45, 65, 20, 5)
                prediction_output.value = initial_pred[0]
                risk_gauge.value = initial_pred[1]
            
            with gr.TabItem("💰 ROI Bem-estar"):
                gr.Markdown("### 🧮 Simulador de Retorno sobre Investimento")
                
                with gr.Row():
                    with gr.Column():
                        investment = gr.Number(value=50000, label="💰 Investimento em Bem-estar (R$)")
                        cost_reduction = gr.Number(value=25000, label="📉 Redução de Custos (R$/ano)")
                        productivity_gain = gr.Slider(0, 30, value=10, label="📈 Ganho de Produtividade (%)")
                        employees = gr.Number(value=50, label="👥 Número de Colaboradores Impactados")
                        avg_salary = gr.Number(value=5000, label="💵 Salário Médio Mensal (R$)")
                    
                    with gr.Column():
                        roi_output = gr.Markdown()
                        roi_chart = gr.Plot()
                
                def calculate_roi_display(investment, cost_reduction, productivity_gain, employees, avg_salary):
                    roi, payback, annual_savings = calculate_roi(investment, cost_reduction, productivity_gain, employees, avg_salary)
                    
                    # Gráfico de barras
                    categories = ['Investimento', 'Economia Anual', 'Retorno Líquido']
                    values = [investment, annual_savings, annual_savings - investment]
                    colors = ['#FF6B6B', '#51CF66', '#339AF0']
                    
                    fig_roi = px.bar(
                        x=categories, 
                        y=values,
                        title="📊 Análise de Investimento vs Retorno",
                        color=categories,
                        color_discrete_sequence=colors,
                        labels={'y': 'Valor (R$)', 'x': ''}
                    )
                    
                    roi_color = "green" if roi > 0 else "red"
                    
                    return (
                        f"""
                        ### 📈 Resultado do ROI
                        
                        **💸 ROI Anual:** <span style='color:{roi_color}'>{roi:.1f}%</span>
                        
                        **⏱️ Período de Payback:** `{payback:.1f} anos`
                        
                        **💰 Economia Anual:** `R$ {annual_savings:,.0f}`
                        
                        **🏦 Investimento:** `R$ {investment:,.0f}`
                        
                        **📊 Retorno Líquido:** `R$ {annual_savings - investment:,.0f}`
                        """,
                        fig_roi
                    )
                
                roi_inputs = [investment, cost_reduction, productivity_gain, employees, avg_salary]
                for inp in roi_inputs:
                    inp.change(calculate_roi_display, inputs=roi_inputs, outputs=[roi_output, roi_chart])
                
                # Valor inicial
                initial_roi = calculate_roi_display(50000, 25000, 10, 50, 5000)
                roi_output.value = initial_roi[0]
                roi_chart.value = initial_roi[1]
            
            with gr.TabItem("📋 Sobre o Projeto"):
                gr.Markdown("### 🎯 Informações do Projeto")
                
                gr.Markdown(f"""
                ## 📊 SST Dashboard - Portfolio Projecto
                
                **🔗 Repositório:** [{GITHUB_REPO}]({GITHUB_REPO})
                
                **📝 Descrição:** Sistema completo para análise preditiva de métricas de Saúde e Segurança no Trabalho com impacto financeiro.
                
                ### 🚀 Funcionalidades Principais
                
                - ✅ **Dashboard interativo** com métricas de SST em tempo real
                - ✅ **Predição de turnover** com modelos de machine learning
                - ✅ **Cálculo de ROI** para iniciativas de bem-estar
                - ✅ **API REST** completa para integrações
                - ✅ **Deploy automatizado** no Render
                - ✅ **Visualizações avançadas** com Plotly
                
                ### 🛠 Stack Tecnológico
                
                | Camada | Tecnologias |
                |--------|-------------|
                | **Frontend** | Gradio, Plotly, HTML/CSS |
                | **Backend** | FastAPI, Python, Uvicorn |
                | **Machine Learning** | Scikit-learn, XGBoost, Pandas |
                | **Database** | PostgreSQL, SQLAlchemy |
                | **Cache** | Redis |
                | **Deploy** | Render, Docker |
                | **Monitoramento** | Render Dashboard, Logs |
                
                ### 📊 Métricas Analisadas
                
                - 📈 **Taxa de turnover** e rotatividade
                - 😰 **Escore de burnout** e saúde mental
                - 🕒 **Horas extras** e carga de trabalho
                - ⚡ **Produtividade** e desempenho
                - 🏥 **Custos com saúde** e benefícios
                - 🚨 **Acidentes de trabalho** e incidentes
                - 💰 **ROI de programas** de bem-estar
                
                ### 🎯 Casos de Uso
                
                - **Gestores de RH:** Monitorar saúde organizacional
                - **Diretores:** Tomada de decisão baseada em dados
                - **Analistas:** Identificar padrões e tendências
                - **Consultores:** Demonstrar impacto financeiro do bem-estar
                
                **👨‍💻 Desenvolvido por:** Cabicho - Portfolio de Projectos
                """)
        
        gr.Markdown("---")
        gr.Markdown(
            f"""
            **🔗 Serviços no Render:**
            - 📊 [Dashboard](https://sst-dashboard-cabicho.onrender.com) | 
            - 🔌 [API](https://sst-api-cabicho.onrender.com) | 
            - 📚 [Documentação](https://sst-api-cabicho.onrender.com/docs)
            
            **📁 Código Fonte:** [{GITHUB_REPO}]({GITHUB_REPO})
            
            *Portfolio Projecto - Análise de Dados & Machine Learning*
            """
        )
    
    return dashboard

# Criar e configurar o dashboard
demo = create_dashboard()

if __name__ == "__main__":
    if RENDER:
        # Configurações para produção no Render
        demo.launch(
            server_name="0.0.0.0",
            server_port=PORT,
            share=False,
            show_error=True
        )
    else:
        # Configurações para desenvolvimento local
        demo.launch(
            server_name="0.0.0.0",
            server_port=PORT,
            share=True,
            debug=True,
            show_error=True
        )
