#!/usr/bin/env python3
"""
Análise simplificada para dados de Moçambique
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import json
import os
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data/mozambique/analise.log')
        ]
    )

def load_data():
    """Carrega os dados coletados"""
    logger = logging.getLogger(__name__)
    logger.info("Carregando dados...")
    
    try:
        df_ine = pd.read_csv('data/mozambique/raw/ine_dados.csv')
        df_misau = pd.read_csv('data/mozambique/raw/misau_dados.csv')
        df_empresas = pd.read_csv('data/mozambique/raw/empresas.csv')
        
        logger.info("✅ Dados carregados com sucesso")
        return df_ine, df_misau, df_empresas
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dados: {e}")
        raise

def analyze_sectoral_data(df_empresas):
    """Análise por setor"""
    logger = logging.getLogger(__name__)
    logger.info("Analisando dados setoriais...")
    
    analise_setor = df_empresas.groupby('setor').agg({
        'burnout_medio': 'mean',
        'acidentes_ano': 'mean',
        'produtividade': 'mean',
        'roi': 'mean',
        'invest_total': 'mean'
    }).round(3)
    
    analise_setor.to_csv('data/mozambique/processed/analise_setorial.csv')
    
    # Gráfico setorial
    fig = px.bar(analise_setor.reset_index(), 
                 x='setor', y=['burnout_medio', 'produtividade'],
                 title='Burnout e Produtividade por Setor',
                 barmode='group')
    fig.write_html('data/mozambique/reports/dashboard_setorial.html')
    
    return analise_setor

def analyze_temporal_trends(df_ine, df_misau):
    """Análise de tendências temporais"""
    logger = logging.getLogger(__name__)
    logger.info("Analisando tendências temporais...")
    
    # Gráfico de tendências
    fig = px.line(df_misau, x='ano', y=['casos_burnout', 'depressao_trabalho'],
                  title='Casos de Saúde Mental em Moçambique (2018-2023)')
    fig.write_html('data/mozambique/reports/tendencias_saude_mental.html')
    
    fig2 = px.line(df_ine, x='ano', y='acidentes_trabalho',
                   title='Acidentes de Trabalho em Moçambique (2018-2023)')
    fig2.write_html('data/mozambique/reports/tendencias_acidentes.html')
    
    return True

def analyze_correlations(df_empresas):
    """Análise de correlações"""
    logger = logging.getLogger(__name__)
    logger.info("Analisando correlações...")
    
    # Matriz de correlação
    corr_matrix = df_empresas[['invest_ergonomia', 'invest_saude_mental', 
                              'burnout_medio', 'acidentes_ano', 
                              'produtividade', 'roi']].corr()
    
    corr_matrix.to_csv('data/mozambique/processed/correlacoes.csv')
    
    # Heatmap de correlação
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                    title="Correlações entre Variáveis SSO")
    fig.write_html('data/mozambique/reports/correlacoes.html')
    
    return corr_matrix

def generate_report(df_ine, df_misau, df_empresas, analise_setor, corr_matrix):
    """Gera relatório final"""
    logger = logging.getLogger(__name__)
    logger.info("Gerando relatório final...")
    
    report = {
        'data_analise': pd.Timestamp.now().isoformat(),
        'estatisticas_gerais': {
            'total_empresas': len(df_empresas),
            'roi_medio': float(df_empresas['roi'].mean()),
            'burnout_medio': float(df_empresas['burnout_medio'].mean()),
            'acidentes_medio': float(df_empresas['acidentes_ano'].mean()),
            'crescimento_burnout_5_anos': float(((df_misau['casos_burnout'].iloc[-1] - df_misau['casos_burnout'].iloc[0]) / df_misau['casos_burnout'].iloc[0] * 100))
        },
        'setores_prioritarios': {
            'maior_burnout': analise_setor['burnout_medio'].nlargest(3).index.tolist(),
            'menor_produtividade': analise_setor['produtividade'].nsmallest(3).index.tolist(),
            'melhor_roi': analise_setor['roi'].nlargest(3).index.tolist()
        },
        'correlacoes_significativas': {
            'invest_saude_mental_roi': float(corr_matrix.loc['invest_saude_mental', 'roi']),
            'burnout_produtividade': float(corr_matrix.loc['burnout_medio', 'produtividade']),
            'acidentes_produtividade': float(corr_matrix.loc['acidentes_ano', 'produtividade'])
        },
        'recomendacoes': [
            "Focar em programas de saúde mental nos setores com maior burnout",
            "Investir em ergonomia para reduzir acidentes e aumentar produtividade",
            "Monitorar ROI dos investimentos em SSO para otimizar recursos"
        ]
    }
    
    with open('data/mozambique/reports/relatorio_completo.json', 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Resumo executivo
    resumo = f"""
    RESUMO EXECUTIVO - ANÁLISE SSO MOÇAMBIQUE
    Data: {report['data_analise'][:10]}
    
    DADOS ANALISADOS:
    - {report['estatisticas_gerais']['total_empresas']} empresas
    - Período: 2018-2023
    - ROI médio: {report['estatisticas_gerais']['roi_medio']:.1f}%
    
    PRINCIPAIS ACHADOS:
    1. Setores críticos: {', '.join(report['setores_prioritarios']['maior_burnout'])}
    2. Crescimento burnout: {report['estatisticas_gerais']['crescimento_burnout_5_anos']:+.1f}%
    3. Correlação investimento-ROI: {report['correlacoes_significativas']['invest_saude_mental_roi']:.3f}
    
    RECOMENDAÇÕES:
    {chr(10).join(['- ' + rec for rec in report['recomendacoes']])}
    """
    
    with open('data/mozambique/reports/resumo_executivo.txt', 'w') as f:
        f.write(resumo)
    
    logger.info("✅ Relatório gerado com sucesso")

def main():
    """Função principal"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Iniciando análise de dados Moçambique")
        
        # Carregar dados
        df_ine, df_misau, df_empresas = load_data()
        
        # Executar análises
        analise_setor = analyze_sectoral_data(df_empresas)
        analyze_temporal_trends(df_ine, df_misau)
        corr_matrix = analyze_correlations(df_empresas)
        
        # Gerar relatório
        generate_report(df_ine, df_misau, df_empresas, analise_setor, corr_matrix)
        
        logger.info("🎉 Análise concluída com sucesso!")
        print("\n📊 Resultados disponíveis em:")
        print("   - data/mozambique/reports/dashboard_setorial.html")
        print("   - data/mozambique/reports/relatorio_completo.json")
        print("   - data/mozambique/reports/resumo_executivo.txt")
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
        raise

if __name__ == "__main__":
    main()
