import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from src.data_loader import DataLoader
from src.model import MulticlassModel
import os

# Configuração do tema
THEME = "soft"

class MulticlassGradioDashboard:
    def __init__(self):
        self.data_loader = DataLoader()
        self.model = MulticlassModel()
        self.data = self.data_loader.load_public_data()
        
    def criar_dashboard_estrategico(self, segmentos, periodo):
        """Painel estratégico para C-Level"""
        dados_filtrados = self.data[self.data['segmento'].isin(segmentos)]
        
        # KPIs Estratégicos
        roi_medio = dados_filtrados['roi_esperado'].mean()
        crescimento_medio = dados_filtrados['crescimento_projetado'].mean()
        valor_total = dados_filtrados['valor_estimado'].sum()
        
        # Gráfico 1: Mapa de Calor de Segmentos
        fig_segmentos = px.treemap(
            dados_filtrados,
            path=['segmento', 'classe_predita'],
            values='valor_estimado',
            color='crescimento_projetado',
            color_continuous_scale='RdYlGn',
            title='Mapa de Valor por Segmento Estratégico'
        )
        
        # Gráfico 2: Análise de Portfolio
        fig_portfolio = go.Figure()
        for classe in dados_filtrados['classe_predita'].unique():
            dados_classe = dados_filtrados[dados_filtrados['classe_predita'] == classe]
            fig_portfolio.add_trace(go.Scatter(
                x=dados_classe['potencial_mercado'],
                y=dados_classe['roi_esperado'],
                mode='markers',
                name=classe,
                marker=dict(
                    size=dados_classe['tamanho_oportunidade']/10000,
                    sizemin=4
                )
            ))
        
        fig_portfolio.update_layout(
            title='Análise Strategic Portfolio - Potencial vs ROI',
            xaxis_title='Potencial de Mercado',
            yaxis_title='ROI Esperado (%)'
        )
        
        # Recomendações Estratégicas
        recomendacoes = self.gerar_recomendacoes_estrategicas(dados_filtrados)
        
        return (
            f"**ROI Médio:** {roi_medio:.1f}% | "
            f"**Crescimento:** {crescimento_medio:.1f}% | "
            f"**Valor Total:** R$ {valor_total:,.0f}",
            fig_segmentos,
            fig_portfolio,
            recomendacoes
        )
    
    def criar_dashboard_tatico(self, canal, metricas):
        """Painel tático para gerência"""
        dados_filtrados = self.data.copy()
        
        # KPIs Táticos
        conversao = np.random.uniform(35, 50)
        cac = np.random.uniform(120, 180)
        ltv = np.random.uniform(1800, 2500)
        
        # Gráfico de Performance de Canais
        fig_canais = px.sunburst(
            self.data,
            path=['segmento', 'classe_predita'],
            values='valor_estimado',
            color='roi_esperado',
            title='Performance por Segmento e Classe'
        )
        
        # Gráfico de Evolução Temporal
        fig_evolucao = px.line(
            self.criar_dados_temporais(),
            x='mes',
            y='valor',
            color='classe',
            title='Evolução Mensal por Classe'
        )
        
        return (
            f"**Conversão:** {conversao:.1f}% | "
            f"**CAC:** R$ {cac:.0f} | "
            f"**LTV:** R$ {ltv:.0f}",
            fig_canais,
            fig_evolucao
        )
    
    def criar_dashboard_operacional(self, alertas_ativos):
        """Painel operacional para execução"""
        # Simular dados em tempo real
        leads_prioritarios = self.data.nlargest(5, 'valor_estimado')
        alertas = self.gerar_alertas_operacionais()
        
        # Tabela de Leads Prioritários
        tabela_leads = leads_prioritarios[['segmento', 'valor_estimado', 'classe_predita', 'roi_esperado']]
        
        # Gráfico de Ações Imediatas
        fig_acoes = px.bar(
            alertas,
            x='prioridade',
            y='quantidade',
            color='tipo',
            title='Alertas e Ações por Prioridade'
        )
        
        # Lista de Ações Recomendadas
        acoes_recomendadas = self.gerar_acoes_instantaneas()
        
        return tabela_leads, fig_acoes, acoes_recomendadas
    
    def criar_dados_temporais(self):
        """Criar dados temporais para análise"""
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
        classes = self.data['classe_predita'].unique()
        
        dados_temp = []
        for mes in meses:
            for classe in classes:
                dados_temp.append({
                    'mes': mes,
                    'classe': classe,
                    'valor': np.random.uniform(50000, 200000)
                })
        
        return pd.DataFrame(dados_temp)
    
    def gerar_recomendacoes_estrategicas(self, dados):
        """Gerar recomendações estratégicas baseadas nos dados"""
        recomendacoes = [
            "🔵 **Alta Prioridade:** Aumentar investimento em segmentos com ROI > 25%",
            "🟢 **Média Prioridade:** Expandir para mercados emergentes identificados",
            "🟡 **Baixa Prioridade:** Otimizar custos em segmentos de baixo crescimento"
        ]
        return "\n\n".join(recomendacoes)
    
    def gerar_alertas_operacionais(self):
        """Gerar alertas operacionais"""
        return pd.DataFrame({
            'prioridade': ['Alta', 'Alta', 'Média', 'Média', 'Baixa'],
            'quantidade': [3, 5, 8, 6, 12],
            'tipo': ['Oportunidade', 'Risco', 'Oportunidade', 'Manutenção', 'Monitoramento']
        })
    
    def gerar_acoes_instantaneas(self):
        """Gerar ações instantâneas para time operacional"""
        acoes = [
            "📞 **Contatar Lead:** Empresa XYZ - Potencial R$ 250k",
            "🎯 **Proposta:** Cliente ABC - Renewal em 30 dias", 
            "⚠️ **Follow-up:** Cliente DEF - Atraso no pagamento",
            "🚀 **Upsell:** Cliente GHI - Produto Premium",
            "📊 **Análise:** Cliente JKL - Comportamento alterado"
        ]
        return "\n".join(acoes)
    
    def criar_interface(self):
        """Criar interface Gradio completa"""
        
        with gr.Blocks(theme=THEME, title="Sistema Multiclasse Estratégico") as dashboard:
            gr.Markdown(
                """
                # 🎯 Sistema de Classificação Multiclasse Estratégico
                **Dashboard Multi-nível para Tomada de Decisão Baseada em IA**
                """
            )
            
            with gr.Tabs() as tabs:
                # TAB 1: PAINEL ESTRATÉGICO
                with gr.TabItem("🎯 Estratégico (C-Level)"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            segmentos_estrategico = gr.CheckboxGroup(
                                choices=list(self.data['segmento'].unique()),
                                value=list(self.data['segmento'].unique())[:2],
                                label="Segmentos de Foco"
                            )
                            periodo_estrategico = gr.Dropdown(
                                choices=["Último Trimestre", "Último Semestre", "Último Ano"],
                                value="Último Trimestre",
                                label="Período de Análise"
                            )
                            btn_estrategico = gr.Button("Atualizar Análise Estratégica", variant="primary")
                        
                        with gr.Column(scale=2):
                            kpis_estrategico = gr.Markdown()
                    
                    with gr.Row():
                        with gr.Column():
                            grafico_segmentos = gr.Plot(label="Mapa de Segmentos")
                        with gr.Column():
                            grafico_portfolio = gr.Plot(label="Análise de Portfolio")
                    
                    with gr.Row():
                        recomendacoes_estrategico = gr.Markdown(label="Recomendações Estratégicas")
                
                # TAB 2: PAINEL TÁTICO
                with gr.TabItem("📊 Tático (Gerência)"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            canal_tatico = gr.Dropdown(
                                choices=["Marketing Digital", "Vendas Diretas", "Parceiros", "Todos"],
                                value="Todos",
                                label="Canal de Vendas"
                            )
                            metricas_tatico = gr.CheckboxGroup(
                                choices=["Conversão", "CAC", "LTV", "ROI"],
                                value=["Conversão", "ROI"],
                                label="Métricas Principais"
                            )
                            btn_tatico = gr.Button("Atualizar Métricas", variant="primary")
                        
                        with gr.Column(scale=2):
                            kpis_tatico = gr.Markdown()
                    
                    with gr.Row():
                        with gr.Column():
                            grafico_canais = gr.Plot(label="Performance por Canal")
                        with gr.Column():
                            grafico_evolucao = gr.Plot(label="Evolução Temporal")
                
                # TAB 3: PAINEL OPERACIONAL
                with gr.TabItem("⚡ Operacional (Execução)"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            alertas_operacional = gr.CheckboxGroup(
                                choices=["Oportunidades", "Riscos", "Follow-ups", "Todos"],
                                value=["Oportunidades", "Riscos"],
                                label="Tipos de Alertas"
                            )
                            btn_operacional = gr.Button("Atualizar Alertas", variant="primary")
                        
                        with gr.Column(scale=2):
                            tabela_leads = gr.Dataframe(
                                label="Leads Prioritários",
                                headers=["Segmento", "Valor Estimado", "Classe", "ROI"],
                                datatype=["str", "number", "str", "number"]
                            )
                    
                    with gr.Row():
                        with gr.Column():
                            grafico_alertas = gr.Plot(label="Distribuição de Alertas")
                        with gr.Column():
                            acoes_operacional = gr.Markdown(label="Ações Recomendadas")
            
            # Conectores de Eventos
            btn_estrategico.click(
                fn=self.criar_dashboard_estrategico,
                inputs=[segmentos_estrategico, periodo_estrategico],
                outputs=[kpis_estrategico, grafico_segmentos, grafico_portfolio, recomendacoes_estrategico]
            )
            
            btn_tatico.click(
                fn=self.criar_dashboard_tatico,
                inputs=[canal_tatico, metricas_tatico],
                outputs=[kpis_tatico, grafico_canais, grafico_evolucao]
            )
            
            btn_operacional.click(
                fn=self.criar_dashboard_operacional,
                inputs=[alertas_operacional],
                outputs=[tabela_leads, grafico_alertas, acoes_operacional]
            )
            
            # Inicializar com dados padrão
            dashboard.load(
                fn=self.criar_dashboard_estrategico,
                inputs=[segmentos_estrategico, periodo_estrategico],
                outputs=[kpis_estrategico, grafico_segmentos, grafico_portfolio, recomendacoes_estrategico]
            )
        
        return dashboard

# Função principal
def main():
    dashboard_app = MulticlassGradioDashboard()
    app = dashboard_app.criar_interface()
    return app

if __name__ == "__main__":
    app = main()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )