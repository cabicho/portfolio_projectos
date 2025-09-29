import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class GradioVisualizations:
    @staticmethod
    def criar_grafico_estrategico(dados, nivel):
        """Criar visualizações para painel estratégico"""
        if nivel == "segmentos":
            fig = px.treemap(
                dados,
                path=['segmento', 'classe_predita'],
                values='valor_estimado',
                color='crescimento_projetado',
                title='Distribuição Estratégica por Segmento'
            )
        else:
            fig = px.scatter(
                dados,
                x='potencial_mercado',
                y='roi_esperado',
                color='classe_predita',
                size='valor_estimado',
                title='Portfolio Estratégico'
            )
        return fig
    
    @staticmethod
    def criar_grafico_tatico(dados, tipo):
        """Criar visualizações para painel tático"""
        if tipo == "canais":
            fig = px.bar(
                dados.groupby('segmento').agg({'valor_estimado': 'sum'}).reset_index(),
                x='segmento',
                y='valor_estimado',
                title='Performance por Segmento'
            )
        else:
            fig = px.line(
                dados.groupby('classe_predita').agg({'roi_esperado': 'mean'}).reset_index(),
                x='classe_predita',
                y='roi_esperado',
                title='ROI Médio por Classe'
            )
        return fig