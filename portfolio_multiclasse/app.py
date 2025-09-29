import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.data_loader import DataLoader
from src.model import MulticlassModel
from src.visualizations import create_strategic_visualizations
import os
import base64

# Configuração da página para melhor performance
st.set_page_config(
    page_title="Sistema Multiclasse Estratégico",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache para melhor performance no Render
@st.cache_data(show_spinner=False)
def load_data():
    """Carrega dados com cache para performance"""
    loader = DataLoader()
    return loader.load_public_data()

@st.cache_resource(show_spinner=False)
def load_model():
    """Carrega modelo com cache"""
    return MulticlassModel()

def add_logo():
    """Adiciona logo personalizado"""
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=200)

class MulticlassDashboard:
    def __init__(self):
        self.data = load_data()
        self.model = load_model()
        
    def run(self):
        # Sidebar com navegação
        add_logo()
        st.sidebar.title("🧭 Navegação Estratégica")
        
        # Seleção de nível de acesso
        nivel_acesso = st.sidebar.radio(
            "Selecione seu Nível:",
            ["🎯 Estratégico", "📊 Tático", "⚡ Operacional"],
            index=0
        )
        
        # Filtros dinâmicos
        st.sidebar.subheader("🔍 Filtros de Análise")
        segmentos = st.sidebar.multiselect(
            "Segmentos:",
            options=self.data['segmento'].unique(),
            default=self.data['segmento'].unique()[:2]
        )
        
        # Aplicar filtros
        dados_filtrados = self.data[self.data['segmento'].isin(segmentos)]
        
        # Renderizar painel baseado no nível
        if nivel_acesso == "🎯 Estratégico":
            self.render_strategic_panel(dados_filtrados)
        elif nivel_acesso == "📊 Tático":
            self.render_tactical_panel(dados_filtrados)
        else:
            self.render_operational_panel(dados_filtrados)
    
    def render_strategic_panel(self, data):
        st.title("🎯 Painel Estratégico - Visão C-Level")
        
        # KPIs em colunas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "ROI Portfolio", 
                "24.3%", 
                "+5.2%",
                help="Retorno sobre investimento do portfólio atual"
            )
        
        with col2:
            st.metric(
                "Market Share", 
                "18.7%", 
                "+2.1%",
                help="Participação de mercado total"
            )
        
        with col3:
            st.metric(
                "Eficiência Capital", 
                "32.1%", 
                "+8.7%",
                help="Eficiência na alocação de capital"
            )
        
        with col4:
            st.metric(
                "Crescimento Estratégico", 
                "15.8%", 
                "+3.4%",
                help="Taxa de crescimento em mercados estratégicos"
            )
        
        # Visualizações estratégicas
        st.subheader("📈 Análise de Portfolio Estratégico")
        
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            fig_segmentos = self.create_segment_heatmap(data)
            st.plotly_chart(fig_segmentos, use_container_width=True)
        
        with col_viz2:
            fig_portfolio = self.create_portfolio_analysis(data)
            st.plotly_chart(fig_portfolio, use_container_width=True)
        
        # Recomendações estratégicas
        st.subheader("💡 Recomendações Estratégicas")
        self.show_strategic_recommendations(data)
    
    def create_segment_heatmap(self, data):
        """Cria mapa de calor de segmentos"""
        segment_summary = data.groupby('segmento').agg({
            'valor_estimado': 'sum',
            'crescimento_projetado': 'mean',
            'roi_esperado': 'mean'
        }).reset_index()
        
        fig = px.treemap(
            segment_summary,
            path=['segmento'],
            values='valor_estimado',
            color='crescimento_projetado',
            color_continuous_scale='RdYlGn',
            title='Mapa de Valor por Segmento Estratégico'
        )
        return fig
    
    def create_portfolio_analysis(self, data):
        """Cria análise de portfolio"""
        fig = go.Figure()
        
        # Agrupar por classe predita
        for classe in data['classe_predita'].unique():
            dados_classe = data[data['classe_predita'] == classe]
            fig.add_trace(go.Scatter(
                x=dados_classe['potencial_mercado'],
                y=dados_classe['roi_esperado'],
                mode='markers',
                name=classe,
                marker=dict(
                    size=dados_classe['tamanho_oportunidade'],
                    sizemode='area',
                    sizeref=2.*max(dados_classe['tamanho_oportunidade'])/(40.**2),
                    sizemin=4
                )
            ))
        
        fig.update_layout(
            title='Análise Strategic Portfolio - Potencial vs ROI',
            xaxis_title='Potencial de Mercado',
            yaxis_title='ROI Esperado (%)',
            hovermode='closest'
        )
        return fig
    
    def show_strategic_recommendations(self, data):
        """Exibe recomendações estratégicas"""
        recommendations = [
            {
                "prioridade": "Alta",
                "categoria": "Alocação de Capital",
                "recomendacao": "Aumentar investimento em segmento B2B Enterprise em 25%",
                "impacto_esperado": "+15% ROI",
                "prazo": "Q1 2024"
            },
            {
                "prioridade": "Média",
                "categoria": "Expansão de Mercado",
                "recomendacao": "Explorar mercado LATAM com foco em Brasil e México",
                "impacto_esperado": "+8% Market Share",
                "prazo": "Q2 2024"
            },
            {
                "prioridade": "Alta",
                "categoria": "Otimização de Portfolio",
                "recomendacao": "Descontinuar produtos com ROI < 5%",
                "impacto_esperado": "+12% Eficiência",
                "prazo": "Q1 2024"
            }
        ]
        
        rec_df = pd.DataFrame(recommendations)
        st.dataframe(
            rec_df,
            column_config={
                "prioridade": st.column_config.TextColumn("Prioridade"),
                "categoria": st.column_config.TextColumn("Categoria"),
                "recomendacao": st.column_config.TextColumn("Recomendação"),
                "impacto_esperado": st.column_config.TextColumn("Impacto Esperado"),
                "prazo": st.column_config.TextColumn("Prazo")
            },
            hide_index=True,
            use_container_width=True
        )
    
    def render_tactical_panel(self, data):
        st.title("📊 Painel Tático - Visão Gerencial")
        # Implementação similar para nível tático
        pass
    
    def render_operational_panel(self, data):
        st.title("⚡ Painel Operacional - Visão Execução")
        # Implementação similar para nível operacional
        pass

# Ponto de entrada da aplicação
if __name__ == "__main__":
    # Verifica se está rodando no Render
    if 'RENDER' in os.environ:
        st.info("🚀 Aplicação rodando no Render Cloud")
    
    dashboard = MulticlassDashboard()
    dashboard.run()