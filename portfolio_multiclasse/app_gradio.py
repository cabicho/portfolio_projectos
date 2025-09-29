import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from src.data_loader import DataLoader
from src.model import MulticlassModel

class MulticlassGradioDashboard:
    def __init__(self):
        self.data_loader = DataLoader()
        self.model = MulticlassModel()
        self.data = self.data_loader.load_public_data()
        
        # Configurações para Render
        self.server_port = int(os.getenv('GRADIO_SERVER_PORT', '7860'))
        self.server_name = os.getenv('GRADIO_SERVER_NAME', '0.0.0.0')
        
    def criar_dashboard_estrategico(self, segmentos, periodo):
        """Painel estratégico para C-Level"""
        dados_filtrados = self.data[self.data['segmento'].isin(segmentos)]
        
        # KPIs Estratégicos
        roi_medio = dados_filtrados['roi_esperado'].mean()
        crescimento_medio = dados_filtrados['crescimento_projetado'].mean()
        valor_total = dados_filtrados['valor_estimado'].sum()
        
        # Gráfico 1: Mapa de Segmentos
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
            title='Análise Strategic Portfolio',
            xaxis_title='Potencial de Mercado',
            yaxis_title='ROI Esperado (%)'
        )
        
        # Recomendações
        recomendacoes = self.gerar_recomendacoes_estrategicas(dados_filtrados)
        
        return (
            f"**ROI Médio:** {roi_medio:.1f}% | "
            f"**Crescimento:** {crescimento_medio:.1f}% | "
            f"**Valor Total:** R$ {valor_total:,.0f}",
            fig_segmentos,
            fig_portfolio,
            recomendacoes
        )
    
    def criar_dashboard_tatico(self, canal, metrica):
        """Painel tático para gerência"""
        dados_filtrados = self.data.copy()
        
        # KPIs Táticos
        conversao = np.random.uniform(35, 50)
        cac = np.random.uniform(120, 180)
        ltv = np.random.uniform(1800, 2500)
        
        # Gráfico de Performance
        fig_canais = px.sunburst(
            self.data,
            path=['segmento', 'classe_predita'],
            values='valor_estimado',
            color='roi_esperado',
            title='Performance por Segmento e Classe'
        )
        
        # Gráfico de Evolução
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
    
    def criar_dashboard_operacional(self, tipo_alerta):
        """Painel operacional para execução"""
        leads_prioritarios = self.data.nlargest(5, 'valor_estimado')
        alertas = self.gerar_alertas_operacionais()
        
        # Tabela de Leads
        tabela_leads = leads_prioritarios[[
            'segmento', 'valor_estimado', 'classe_predita', 'roi_esperado'
        ]]
        
        # Gráfico de Alertas
        fig_alertas = px.bar(
            alertas,
            x='prioridade',
            y='quantidade',
            color='tipo',
            title='Alertas por Prioridade'
        )
        
        # Ações Recomendadas
        acoes = self.gerar_acoes_instantaneas()
        
        return tabela_leads, fig_alertas, acoes
    
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
        recomendacoes = [
            "🎯 **Alta Prioridade:** Investir em segmentos com ROI > 25%",
            "📈 **Média Prioridade:** Expandir para mercados emergentes", 
            "⚡ **Baixa Prioridade:** Otimizar custos operacionais"
        ]
        return "\n\n".join(recomendacoes)
    
    def gerar_alertas_operacionais(self):
        return pd.DataFrame({
            'prioridade': ['Alta', 'Alta', 'Média', 'Média', 'Baixa'],
            'quantidade': [3, 5, 8, 6, 12],
            'tipo': ['Oportunidade', 'Risco', 'Oportunidade', 'Manutenção', 'Monitoramento']
        })
    
    def gerar_acoes_instantaneas(self):
        acoes = [
            "📞 **Contatar:** Empresa XYZ - Potencial R$ 250k",
            "🎯 **Proposta:** Cliente ABC - Renewal em 30 dias", 
            "⚠️ **Follow-up:** Cliente DEF - Atraso pagamento",
            "🚀 **Upsell:** Cliente GHI - Produto Premium"
        ]
        return "\n".join(acoes)
    
    def criar_interface(self):
        """Criar interface Gradio completa"""
        with gr.Blocks(
            theme=gr.themes.Soft(),
            title="Sistema Multiclasse Estratégico - Render"
        ) as dashboard:
            
            gr.Markdown(
                """
                # 🎯 Sistema de Classificação Multiclasse Estratégico
                **Deploy Profissional no Render Cloud**
                """
            )
            
            with gr.Tabs() as tabs:
                # TAB ESTRATÉGICO
                with gr.TabItem("🎯 Estratégico"):
                    with gr.Row():
                        segmentos = gr.CheckboxGroup(
                            choices=list(self.data['segmento'].unique()),
                            value=list(self.data['segmento'].unique())[:2],
                            label="Segmentos"
                        )
                        periodo = gr.Dropdown(
                            choices=["Trimestre", "Semestre", "Ano"],
                            value="Trimestre",
                            label="Período"
                        )
                    
                    btn_estrategico = gr.Button("Analisar", variant="primary")
                    kpis_estrategico = gr.Markdown()
                    
                    with gr.Row():
                        grafico_segmentos = gr.Plot()
                        grafico_portfolio = gr.Plot()
                    
                    recomendacoes = gr.Markdown()
                
                # TAB TÁTICO
                with gr.TabItem("📊 Tático"):
                    with gr.Row():
                        canal = gr.Dropdown(
                            choices=["Marketing", "Vendas", "Parceiros", "Todos"],
                            value="Todos",
                            label="Canal"
                        )
                        metrica = gr.Dropdown(
                            choices=["Conversão", "ROI", "Crescimento"],
                            value="ROI",
                            label="Métrica Principal"
                        )
                    
                    btn_tatico = gr.Button("Analisar", variant="primary")
                    kpis_tatico = gr.Markdown()
                    
                    with gr.Row():
                        grafico_canais = gr.Plot()
                        grafico_evolucao = gr.Plot()
                
                # TAB OPERACIONAL
                with gr.TabItem("⚡ Operacional"):
                    tipo_alerta = gr.CheckboxGroup(
                        choices=["Oportunidades", "Riscos", "Follow-ups"],
                        value=["Oportunidades"],
                        label="Alertas"
                    )
                    
                    btn_operacional = gr.Button("Atualizar", variant="primary")
                    
                    with gr.Row():
                        tabela_leads = gr.Dataframe(
                            headers=["Segmento", "Valor", "Classe", "ROI"]
                        )
                        grafico_alertas = gr.Plot()
                    
                    acoes_recomendadas = gr.Markdown()
            
            # Event Handlers
            btn_estrategico.click(
                self.criar_dashboard_estrategico,
                [segmentos, periodo],
                [kpis_estrategico, grafico_segmentos, grafico_portfolio, recomendacoes]
            )
            
            btn_tatico.click(
                self.criar_dashboard_tatico,
                [canal, metrica],
                [kpis_tatico, grafico_canais, grafico_evolucao]
            )
            
            btn_operacional.click(
                self.criar_dashboard_operacional,
                [tipo_alerta],
                [tabela_leads, grafico_alertas, acoes_recomendadas]
            )
        
        return dashboard
    
    def launch(self):
        """Iniciar aplicação com configurações do Render"""
        app = self.criar_interface()
        app.launch(
            server_name=self.server_name,
            server_port=self.server_port,
            share=False,
            debug=False  # False para produção
        )

# Ponto de entrada otimizado para Render
if __name__ == "__main__":
    print("🚀 Iniciando Sistema Multiclasse no Render...")
    dashboard = MulticlassGradioDashboard()
    dashboard.launch()