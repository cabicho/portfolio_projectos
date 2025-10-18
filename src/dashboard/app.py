import pandas as pd
import numpy as np
import xlsxwriter
import csv
from io import BytesIO
import base64
from datetime import datetime, timedelta
import random

# PDF imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

# Dash imports
import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================================================================
# CONFIGURAÇÃO E GERAÇÃO DE DADOS
# =============================================================================

def gerar_dados_portfolio(n_clientes=500):
    """Gerar dados simulados do portfolio de crédito"""
    np.random.seed(42)
    random.seed(42)
    
    segmentos = ['SME', 'Individual', 'Corporate']
    riscos = [2, 3, 4, 5]
    
    # Distribuições realistas
    dist_segmentos = {'SME': 0.38, 'Individual': 0.31, 'Corporate': 0.31}
    dist_riscos = {2: 0.06, 3: 0.10, 4: 0.16, 5: 0.68}
    
    dados = []
    for i in range(1, n_clientes + 1):
        segmento = random.choices(segmentos, weights=[dist_segmentos[s] for s in segmentos])[0]
        
        # Valores de contrato por segmento
        if segmento == 'Individual':
            valor_contrato = random.uniform(5000, 30000)
        elif segmento == 'SME':
            valor_contrato = random.uniform(15000, 50000)
        else:  # Corporate
            valor_contrato = random.uniform(25000, 80000)
            
        dias_atraso = random.randint(0, 120)
        risco_credito = random.choices(riscos, weights=[dist_riscos[r] for r in riscos])[0]
        satisfacao = random.uniform(1.0, 5.0)
        
        # Definir segmento do cliente baseado no risco e dias de atraso
        if risco_credito <= 2 and dias_atraso <= 15:
            segmento_cliente = 'Baixo Risco'
        elif risco_credito == 3 and dias_atraso <= 30:
            segmento_cliente = 'Médio Risco'
        elif dias_atraso > 60:
            segmento_cliente = 'Atraso Crítico'
        else:
            segmento_cliente = 'Alto Risco'
            
        dados.append({
            'cliente_id': i,
            'segmento': segmento,
            'valor_contrato': round(valor_contrato, 2),
            'dias_atraso': dias_atraso,
            'risco_credito': risco_credito,
            'satisfacao_cliente': round(satisfacao, 2),
            'segmento_cliente': segmento_cliente
        })
    
    df = pd.DataFrame(dados)
    print(f"✅ Dados gerados: {len(df)} clientes")
    print(f"📊 Segmentos: {dict(df['segmento'].value_counts())}")
    print(f"🎯 Riscos: {dict(df['risco_credito'].value_counts().sort_index())}")
    
    return df

# =============================================================================
# FUNÇÕES DE ANÁLISE E INSIGHTS DINÂMICOS
# =============================================================================

def generate_segment_insights(filtered_df, original_df):
    """Gerar insights dinâmicos sobre segmentos baseados nos dados filtrados"""
    if len(filtered_df) == 0:
        return "Nenhum dado disponível para os filtros selecionados."
    
    total_original = len(original_df)
    total_filtrado = len(filtered_df)
    percentual_filtrado = (total_filtrado / total_original) * 100
    
    # Análise por segmento
    segment_analysis = filtered_df['segmento'].value_counts()
    dominant_segment = segment_analysis.index[0] if len(segment_analysis) > 0 else "N/A"
    dominant_segment_pct = (segment_analysis.iloc[0] / total_filtrado * 100) if len(segment_analysis) > 0 else 0
    
    insights = [
        f"📊 **Visão Geral**: {total_filtrado} clientes ({percentual_filtrado:.1f}% do total)",
        f"🎯 **Segmento Dominante**: {dominant_segment} ({dominant_segment_pct:.1f}% dos clientes filtrados)"
    ]
    
    return insights

def generate_risk_insights(filtered_df):
    """Gerar insights sobre riscos baseados nos dados filtrados"""
    if len(filtered_df) == 0:
        return "Nenhum dado disponível para análise de risco."
    
    # Análise de risco
    risco_analysis = filtered_df['risco_credito'].value_counts().sort_index()
    risco_medio = filtered_df['risco_credito'].mean()
    
    # Clientes de alto risco
    alto_risco_count = len(filtered_df[filtered_df['segmento_cliente'] == 'Alto Risco'])
    atraso_critico_count = len(filtered_df[filtered_df['segmento_cliente'] == 'Atraso Crítico'])
    total_risco_elevado = alto_risco_count + atraso_critico_count
    pct_risco_elevado = (total_risco_elevado / len(filtered_df)) * 100
    
    insights = [
        f"⚠️ **Risco Médio**: {risco_medio:.1f}/5",
        f"🔴 **Clientes de Alto Risco**: {alto_risco_count} ({alto_risco_count/len(filtered_df)*100:.1f}%)",
        f"🚨 **Atraso Crítico**: {atraso_critico_count} ({atraso_critico_count/len(filtered_df)*100:.1f}%)",
        f"📈 **Total Risco Elevado**: {total_risco_elevado} clientes ({pct_risco_elevado:.1f}%)"
    ]
    
    return insights

def generate_performance_insights(filtered_df):
    """Gerar insights de performance baseados nos dados filtrados"""
    if len(filtered_df) == 0:
        return "Nenhum dado disponível para análise de performance."
    
    # Métricas de performance
    valor_total = filtered_df['valor_contrato'].sum()
    valor_medio = filtered_df['valor_contrato'].mean()
    dias_atraso_medio = filtered_df['dias_atraso'].mean()
    satisfacao_media = filtered_df['satisfacao_cliente'].mean()
    
    # Análise de concentração
    top_10_valor = filtered_df.nlargest(max(1, len(filtered_df)//10), 'valor_contrato')
    concentracao_top_10 = (top_10_valor['valor_contrato'].sum() / valor_total * 100) if valor_total > 0 else 0
    
    insights = [
        f"💰 **Valor Total**: R$ {valor_total:,.2f}",
        f"📊 **Ticket Médio**: R$ {valor_medio:,.2f}",
        f"⏰ **Atraso Médio**: {dias_atraso_medio:.1f} dias",
        f"😊 **Satisfação**: {satisfacao_media:.2f}/5",
        f"🎯 **Concentração Top 10%**: {concentracao_top_10:.1f}% do valor total"
    ]
    
    return insights

def generate_alerts_insights(filtered_df):
    """Gerar alertas e recomendações baseados nos dados filtrados"""
    if len(filtered_df) == 0:
        return "Nenhum alerta para os filtros selecionados."
    
    alerts = []
    
    # Alertas baseados em métricas
    atraso_critico_count = len(filtered_df[filtered_df['segmento_cliente'] == 'Atraso Crítico'])
    if atraso_critico_count > 0:
        alerts.append(f"🚨 **Urgente**: {atraso_critico_count} cliente(s) em Atraso Crítico necessitam de ação imediata")
    
    alto_risco_count = len(filtered_df[filtered_df['segmento_cliente'] == 'Alto Risco'])
    if alto_risco_count > len(filtered_df) * 0.3:  # Mais de 30% em alto risco
        alerts.append(f"⚠️ **Atenção**: {alto_risco_count} cliente(s) em Alto Risco ({alto_risco_count/len(filtered_df)*100:.1f}% do portfolio filtrado)")
    
    # Alertas de satisfação
    satisfacao_baixa_count = len(filtered_df[filtered_df['satisfacao_cliente'] < 2.5])
    if satisfacao_baixa_count > 0:
        alerts.append(f"😟 **Satisfação Baixa**: {satisfacao_baixa_count} cliente(s) com satisfação abaixo de 2.5")
    
    # Alertas de concentração
    if len(filtered_df) > 0:
        maior_cliente_valor = filtered_df['valor_contrato'].max()
        valor_total = filtered_df['valor_contrato'].sum()
        if maior_cliente_valor > valor_total * 0.1:  # Cliente representa mais de 10% do valor
            alerts.append("⚖️ **Concentração**: Um cliente representa mais de 10% do valor total filtrado")
    
    if not alerts:
        alerts.append("✅ **Situação Controlada**: Nenhum alerta crítico identificado")
    
    return alerts

def generate_strategic_recommendations(filtered_df):
    """Gerar recomendações estratégicas baseadas nos dados filtrados"""
    if len(filtered_df) == 0:
        return "Nenhuma recomendação para os filtros selecionados."
    
    recommendations = []
    
    # Análise para recomendações
    risco_medio = filtered_df['risco_credito'].mean()
    dias_atraso_medio = filtered_df['dias_atraso'].mean()
    satisfacao_media = filtered_df['satisfacao_cliente'].mean()
    
    if risco_medio >= 4:
        recommendations.append("🎯 **Foco em Mitigação**: Priorizar ações de redução de risco para clientes com score 4+")
    
    if dias_atraso_medio > 45:
        recommendations.append("⏰ **Gestão de Cobrança**: Revisar processos de cobrança para reduzir atraso médio")
    
    if satisfacao_media < 3:
        recommendations.append("💬 **Melhoria de Relacionamento**: Implementar ações para aumentar satisfação do cliente")
    
    # Recomendações baseadas em segmento
    segment_counts = filtered_df['segmento'].value_counts()
    if len(segment_counts) > 0:
        maior_segmento = segment_counts.index[0]
        recommendations.append(f"📋 **Estratégia Segmentada**: Desenvolver abordagem específica para segmento {maior_segmento}")
    
    if len(recommendations) == 0:
        recommendations.append("📊 **Manutenção**: Manter estratégias atuais, performance dentro dos parâmetros esperados")
    
    return recommendations

# =============================================================================
# FUNÇÕES DE EXPORTAÇÃO CORRIGIDAS
# =============================================================================

def exportar_excel(df, nome_arquivo="clientes_credit_control"):
    """Exportar DataFrame para Excel com formatação profissional - CORRIGIDO"""
    output = BytesIO()
    
    try:
        # CORREÇÃO: Removido o parâmetro 'options' problemático
        with pd.ExcelWriter(output, engine='xlsxwriter', datetime_format='DD/MM/YYYY') as writer:
            # Sheet principal com dados completos
            df.to_excel(writer, sheet_name='Clientes_Detalhado', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Clientes_Detalhado']
            
            # Formatos
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#2E86AB',
                'font_color': 'white',
                'border': 1,
                'font_size': 10
            })
            
            money_format = workbook.add_format({'num_format': 'R$ #,##0.00', 'border': 1})
            integer_format = workbook.add_format({'num_format': '0', 'border': 1})
            float_format = workbook.add_format({'num_format': '0.00', 'border': 1})
            default_format = workbook.add_format({'border': 1})
            
            # Formatar cabeçalho
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Formatar colunas
            for col_num, col_name in enumerate(df.columns):
                if 'valor' in col_name.lower():
                    worksheet.set_column(col_num, col_num, 15, money_format)
                elif any(x in col_name.lower() for x in ['id', 'dias', 'risco']):
                    worksheet.set_column(col_num, col_num, 12, integer_format)
                elif 'satisfacao' in col_name.lower():
                    worksheet.set_column(col_num, col_num, 12, float_format)
                else:
                    worksheet.set_column(col_num, col_num, 15, default_format)
            
            # Auto-filter e congela painel
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
            worksheet.freeze_panes(1, 0)
            
            # Sheet de resumo
            resumo_data = {
                'Métrica': [
                    'Total de Clientes',
                    'Valor Total Contratos (R$)',
                    'Média Valor Contrato (R$)',
                    'Média Dias Atraso',
                    'Média Satisfação',
                    'Clientes Alto Risco',
                    'Clientes Atraso Crítico'
                ],
                'Valor': [
                    len(df),
                    f"R$ {df['valor_contrato'].sum():,.2f}",
                    f"R$ {df['valor_contrato'].mean():,.2f}",
                    f"{df['dias_atraso'].mean():.1f}",
                    f"{df['satisfacao_cliente'].mean():.2f}",
                    len(df[df['segmento_cliente'] == 'Alto Risco']),
                    len(df[df['segmento_cliente'] == 'Atraso Crítico'])
                ]
            }
            
            resumo_df = pd.DataFrame(resumo_data)
            resumo_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            worksheet_resumo = writer.sheets['Resumo']
            worksheet_resumo.set_column('A:A', 25)
            worksheet_resumo.set_column('B:B', 20)
            
        output.seek(0)
        return output
    except Exception as e:
        print(f"Erro ao exportar Excel: {e}")
        return None

def exportar_csv(df):
    """Exportar DataFrame para CSV com encoding correto"""
    output = BytesIO()
    try:
        df.to_csv(output, index=False, encoding='utf-8-sig', sep=';')
        output.seek(0)
        return output
    except Exception as e:
        print(f"Erro ao exportar CSV: {e}")
        return None

def exportar_pdf(df, titulo="Relatório de Clientes - Credit Control Dashboard"):
    """Exportar DataFrame para PDF com layout profissional"""
    output = BytesIO()
    
    try:
        doc = SimpleDocTemplate(output, pagesize=A4, topMargin=0.5*inch)
        elements = []
        
        styles = getSampleStyleSheet()
        
        # Estilo personalizado
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            alignment=1,
            textColor=colors.HexColor('#2E86AB')
        )
        
        # Título
        title = Paragraph(titulo, title_style)
        elements.append(title)
        
        # Informações
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=15,
            alignment=1
        )
        
        info_text = f"Total de clientes: {len(df)} | Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        info_paragraph = Paragraph(info_text, info_style)
        elements.append(info_paragraph)
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Resumo estatístico
        resumo_data = [
            ['Métrica', 'Valor'],
            ['Valor Total Contratos', f"R$ {df['valor_contrato'].sum():,.2f}"],
            ['Média Valor Contrato', f"R$ {df['valor_contrato'].mean():,.2f}"],
            ['Média Dias Atraso', f"{df['dias_atraso'].mean():.1f}"],
            ['Clientes Alto Risco', f"{len(df[df['segmento_cliente'] == 'Alto Risco'])}"],
            ['Clientes Atraso Crítico', f"{len(df[df['segmento_cliente'] == 'Atraso Crítico'])}"]
        ]
        
        resumo_table = Table(resumo_data, colWidths=[200, 100])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(resumo_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Dados dos clientes (limitado)
        colunas_display = [str(col)[:20] + "..." if len(str(col)) > 20 else str(col) for col in df.columns]
        data = [colunas_display]
        
        max_rows_pdf = 50
        df_display = df.head(max_rows_pdf)
        
        for _, row in df_display.iterrows():
            data_row = []
            for val in row:
                if isinstance(val, float):
                    if 'valor' in str(row.name).lower():
                        data_row.append(f"R$ {val:,.2f}")
                    else:
                        data_row.append(f"{val:.2f}")
                else:
                    data_row.append(str(val))
            data.append(data_row)
        
        table = Table(data, repeatRows=1, colWidths=[60, 60, 80, 60, 60, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        elements.append(table)
        
        # Nota sobre limitação
        if len(df) > max_rows_pdf:
            note_style = ParagraphStyle(
                'NoteStyle',
                parent=styles['Normal'],
                fontSize=8,
                spaceBefore=12,
                textColor=colors.grey
            )
            note = Paragraph(f"*Nota: Mostrando {max_rows_pdf} de {len(df)} clientes. Use exportação Excel para dados completos.", note_style)
            elements.append(note)
        
        # Rodapé
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            spaceBefore=20,
            alignment=1,
            textColor=colors.grey
        )
        footer = Paragraph("Credit Control Dashboard - Sistema de Gestão de Risco de Crédito", footer_style)
        elements.append(footer)
        
        doc.build(elements)
        output.seek(0)
        return output
        
    except Exception as e:
        print(f"Erro ao exportar PDF: {e}")
        return None

def criar_download_link(output, filename, text, file_type="excel"):
    """Criar link de download"""
    if output is None:
        return html.Div("Erro ao gerar arquivo", style={'color': 'red', 'padding': '10px'})
    
    try:
        b64 = base64.b64encode(output.getvalue()).decode()
        
        mime_types = {
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'csv': 'text/csv; charset=utf-8',
            'pdf': 'application/pdf'
        }
        
        mime_type = mime_types.get(file_type, 'application/octet-stream')
        
        icons = {'excel': '📊', 'csv': '📝', 'pdf': '📄'}
        icon = icons.get(file_type, '📥')
        
        href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" style="text-decoration: none; color: white; background-color: #2E86AB; padding: 10px 15px; border-radius: 5px; margin: 5px; display: inline-block; font-weight: bold;">{icon} {text}</a>'
        return html.Div(html.Iframe(srcDoc=href, style={"border": "none", "height": "45px", "width": "180px"}))
        
    except Exception as e:
        return html.Div(f"Erro no download: {str(e)}", style={'color': 'red', 'padding': '10px'})

# =============================================================================
# APLICAÇÃO DASH
# =============================================================================

# Inicializar aplicação Dash
app = dash.Dash(
    __name__,
    title="Credit Control Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Gerar dados
df = gerar_dados_portfolio(500)

# CSS personalizado
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .btn-export {
                background-color: #2E86AB;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
                padding: 10px 15px;
                margin: 5px;
                font-size: 14px;
            }
            .btn-export:hover {
                background-color: #1B5E7A;
            }
            .btn-print {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
                padding: 10px 15px;
                margin: 5px;
                font-size: 14px;
            }
            .btn-print:hover {
                background-color: #219653;
            }
            .no-print {
                display: block;
            }
            .insight-card {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #2E86AB;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .alert-card {
                background: #FFF3CD;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #FFC107;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .recommendation-card {
                background: #D1ECF1;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #17A2B8;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            @media print {
                .no-print {
                    display: none !important;
                }
                body {
                    font-size: 12pt;
                }
                .metric-box {
                    break-inside: avoid;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout principal
app.layout = html.Div([
    # Cabeçalho
    html.Div([
        html.H1("🏦 Credit Control Dashboard", 
                style={'color': '#2E86AB', 'marginBottom': '10px'}),
        html.P("Sistema de Gestão e Monitoramento de Risco de Crédito", 
               style={'color': '#666', 'fontSize': '16px'}),
        html.Hr()
    ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white'}),
    
    # Filtros COM SELEÇÃO MÚLTIPLA
    html.Div([
        html.Div([
            html.Label("Segmento:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='filtro-segmento',
                options=[{'label': 'Todos', 'value': 'all'}] + 
                        [{'label': seg, 'value': seg} for seg in sorted(df['segmento'].unique())],
                value=['all'],  # Agora é uma lista
                clearable=False,
                multi=True,  # ATIVA SELEÇÃO MÚLTIPLA
                placeholder="Selecione um ou mais segmentos..."
            )
        ], style={'width': '24%', 'display': 'inline-block', 'margin': '10px'}),
        
        html.Div([
            html.Label("Risco Crédito:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='filtro-risco',
                options=[{'label': 'Todos', 'value': 'all'}] + 
                        [{'label': f'Risco {risco}', 'value': risco} for risco in sorted(df['risco_credito'].unique())],
                value=['all'],  # Agora é uma lista
                clearable=False,
                multi=True,  # ATIVA SELEÇÃO MÚLTIPLA
                placeholder="Selecione um ou mais riscos..."
            )
        ], style={'width': '24%', 'display': 'inline-block', 'margin': '10px'}),
        
        html.Div([
            html.Label("Segmento Cliente:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='filtro-segmento-cliente',
                options=[{'label': 'Todos', 'value': 'all'}] + 
                        [{'label': seg, 'value': seg} for seg in sorted(df['segmento_cliente'].unique())],
                value=['all'],  # Agora é uma lista
                clearable=False,
                multi=True,  # ATIVA SELEÇÃO MÚLTIPLA
                placeholder="Selecione um ou mais segmentos..."
            )
        ], style={'width': '24%', 'display': 'inline-block', 'margin': '10px'}),
        
        html.Div([
            html.Label("Dias Atraso:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='filtro-dias-atraso',
                min=0,
                max=120,
                step=5,
                value=[0, 120],
                marks={0: '0', 30: '30', 60: '60', 90: '90', 120: '120'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'margin': '10px'}),
    ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'margin': '10px'}),
    
    # Métricas
    html.Div([
        html.Div([
            html.H4("💰 Valor Total", style={'color': '#2E86AB'}),
            html.H3(id="valor-total", style={'color': '#1B5E7A'})
        ], className="metric-box", style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'margin': '5px', 'borderRadius': '8px'}),
        
        html.Div([
            html.H4("👥 Total Clientes", style={'color': '#2E86AB'}),
            html.H3(id="total-clientes", style={'color': '#1B5E7A'})
        ], className="metric-box", style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'margin': '5px', 'borderRadius': '8px'}),
        
        html.Div([
            html.H4("⚠️ Alto Risco", style={'color': '#2E86AB'}),
            html.H3(id="alto-risco", style={'color': '#E74C3C'})
        ], className="metric-box", style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'margin': '5px', 'borderRadius': '8px'}),
        
        html.Div([
            html.H4("🔴 Atraso Crítico", style={'color': '#2E86AB'}),
            html.H3(id="atraso-critico", style={'color': '#C0392B'})
        ], className="metric-box", style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'margin': '5px', 'borderRadius': '8px'}),
        
        html.Div([
            html.H4("😊 Satisfação Média", style={'color': '#2E86AB'}),
            html.H3(id="satisfacao-media", style={'color': '#27AE60'})
        ], className="metric-box", style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'margin': '5px', 'borderRadius': '8px'}),
    ], style={'textAlign': 'center', 'margin': '10px'}),
    
    # Análises e Insights Dinâmicos
    html.Div([
        html.H3("🧠 Análises e Insights", style={'color': '#2E86AB', 'marginBottom': '20px'}),
        
        html.Div([
            html.H4("📊 Análise do Portfolio", style={'color': '#2E86AB'}),
            html.Div(id='segment-insights', className='insight-card')
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.H4("⚠️ Análise de Risco", style={'color': '#2E86AB'}),
            html.Div(id='risk-insights', className='insight-card')
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.H4("📈 Performance", style={'color': '#2E86AB'}),
            html.Div(id='performance-insights', className='insight-card')
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'margin': '10px', 'borderRadius': '8px'}),
    
    # Alertas e Recomendações
    html.Div([
        html.Div([
            html.H4("🚨 Alertas e Ações", style={'color': '#2E86AB'}),
            html.Div(id='alerts-insights', className='alert-card')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.H4("💡 Recomendações Estratégicas", style={'color': '#2E86AB'}),
            html.Div(id='recommendations-insights', className='recommendation-card')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'margin': '10px', 'borderRadius': '8px'}),
    
    # Gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-risco-segmento')
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='grafico-valor-atraso')
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '10px'}),
    ]),
    
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-distribuicao-segmento')
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='grafico-satisfacao-risco')
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '10px'}),
    ]),
    
    # Tabela de dados
    html.Div([
        html.H3("📋 Detalhes dos Clientes", style={'color': '#2E86AB'}),
        html.Div(id='info-clientes', style={'marginBottom': '10px'}),
        dash_table.DataTable(
            id='tabela-clientes',
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'fontSize': '12px',
                'fontFamily': 'Arial'
            },
            style_header={
                'backgroundColor': '#2E86AB',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {'filter_query': '{segmento_cliente} = "Atraso Crítico"'},
                    'backgroundColor': '#FFE5E5',
                    'color': 'black'
                },
                {
                    'if': {'filter_query': '{segmento_cliente} = "Alto Risco"'},
                    'backgroundColor': '#FFF4E5',
                    'color': 'black'
                }
            ]
        )
    ], style={'backgroundColor': 'white', 'padding': '20px', 'margin': '10px', 'borderRadius': '8px'}),
    
    # Exportação
    html.Div([
        html.Hr(),
        html.H3("📤 Exportar Relatório", style={'color': '#2E86AB', 'textAlign': 'center'}),
        
        html.Div([
            html.Button("📊 Exportar Excel", 
                       id="btn-export-excel",
                       className="btn-export no-print"),
            
            html.Button("📝 Exportar CSV", 
                       id="btn-export-csv", 
                       className="btn-export no-print"),
            
            html.Button("📄 Exportar PDF", 
                       id="btn-export-pdf",
                       className="btn-export no-print"),
            
            html.Button("🖨️ Imprimir Relatório", 
                       id="btn-print",
                       className="btn-print no-print")
            
        ], style={'textAlign': 'center', 'margin': '20px 0'}),
        
        html.Div(id="download-excel", style={'textAlign': 'center'}),
        html.Div(id="download-csv", style={'textAlign': 'center'}),
        html.Div(id="download-pdf", style={'textAlign': 'center'}),
        
    ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 'margin': '10px', 'borderRadius': '8px'}),
    
    # Rodapé
    html.Div([
        html.Hr(),
        html.P("Credit Control Dashboard | Branch: pipeline-car-dev | Demonstração para vaga Junior Data & Reporting Officer", 
               style={'color': '#666', 'fontSize': '12px', 'textAlign': 'center'})
    ], style={'marginTop': '20px'})
], style={'padding': '10px', 'backgroundColor': '#f5f5f5'}, id='main-container')

# =============================================================================
# CALLBACKS COM SUPORTE A SELEÇÃO MÚLTIPLA
# =============================================================================

def get_filtered_data(segmento=['all'], risco=['all'], segmento_cliente=['all'], dias_atraso_range=[0, 120]):
    """Obter dados filtrados baseado nos filtros aplicados - COM SUPORTE A MÚLTIPLAS SELEÇÕES"""
    filtered_df = df.copy()
    
    # Aplicar filtros com suporte a múltiplas seleções
    if 'all' not in segmento:
        filtered_df = filtered_df[filtered_df['segmento'].isin(segmento)]
    
    if 'all' not in risco:
        filtered_df = filtered_df[filtered_df['risco_credito'].isin(risco)]
    
    if 'all' not in segmento_cliente:
        filtered_df = filtered_df[filtered_df['segmento_cliente'].isin(segmento_cliente)]
    
    # Filtrar por dias de atraso
    filtered_df = filtered_df[
        (filtered_df['dias_atraso'] >= dias_atraso_range[0]) & 
        (filtered_df['dias_atraso'] <= dias_atraso_range[1])
    ]
    
    return filtered_df

# Callback principal para atualizar todas as análises
@app.callback(
    [Output('valor-total', 'children'),
     Output('total-clientes', 'children'),
     Output('alto-risco', 'children'),
     Output('atraso-critico', 'children'),
     Output('satisfacao-media', 'children'),
     Output('info-clientes', 'children'),
     Output('segment-insights', 'children'),
     Output('risk-insights', 'children'),
     Output('performance-insights', 'children'),
     Output('alerts-insights', 'children'),
     Output('recommendations-insights', 'children')],
    [Input('filtro-segmento', 'value'),
     Input('filtro-risco', 'value'),
     Input('filtro-segmento-cliente', 'value'),
     Input('filtro-dias-atraso', 'value')]
)
def update_all_analyses(segmento, risco, segmento_cliente, dias_atraso_range):
    # Garantir que os valores são listas (para compatibilidade)
    segmento = segmento if isinstance(segmento, list) else [segmento]
    risco = risco if isinstance(risco, list) else [risco]
    segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
    
    filtered_df = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
    
    # Métricas básicas
    valor_total = f"R$ {filtered_df['valor_contrato'].sum():,.2f}" if len(filtered_df) > 0 else "R$ 0,00"
    total_clientes = f"{len(filtered_df)}" if len(filtered_df) > 0 else "0"
    alto_risco = f"{len(filtered_df[filtered_df['segmento_cliente'] == 'Alto Risco'])}" if len(filtered_df) > 0 else "0"
    atraso_critico = f"{len(filtered_df[filtered_df['segmento_cliente'] == 'Atraso Crítico'])}" if len(filtered_df) > 0 else "0"
    satisfacao_media = f"{filtered_df['satisfacao_cliente'].mean():.2f}" if len(filtered_df) > 0 else "0,00"
    
    info_text = f"Mostrando {len(filtered_df)} de {len(df)} clientes" if len(filtered_df) > 0 else "Nenhum cliente encontrado"
    
    # Análises dinâmicas
    segment_insights = generate_segment_insights(filtered_df, df)
    risk_insights = generate_risk_insights(filtered_df)
    performance_insights = generate_performance_insights(filtered_df)
    alerts_insights = generate_alerts_insights(filtered_df)
    recommendations_insights = generate_strategic_recommendations(filtered_df)
    
    # Converter análises para componentes HTML
    def create_insight_list(insights):
        if isinstance(insights, str):
            return html.P(insights)
        return html.Ul([html.Li(html.Span(insight, style={'whiteSpace': 'pre-wrap'})) for insight in insights])
    
    return (valor_total, total_clientes, alto_risco, atraso_critico, satisfacao_media, info_text,
            create_insight_list(segment_insights),
            create_insight_list(risk_insights),
            create_insight_list(performance_insights),
            create_insight_list(alerts_insights),
            create_insight_list(recommendations_insights))

# Callback para atualizar tabela
@app.callback(
    Output('tabela-clientes', 'data'),
    [Input('filtro-segmento', 'value'),
     Input('filtro-risco', 'value'),
     Input('filtro-segmento-cliente', 'value'),
     Input('filtro-dias-atraso', 'value')]
)
def update_table(segmento, risco, segmento_cliente, dias_atraso_range):
    # Garantir que os valores são listas
    segmento = segmento if isinstance(segmento, list) else [segmento]
    risco = risco if isinstance(risco, list) else [risco]
    segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
    
    filtered_df = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
    return filtered_df.to_dict('records')

# Callbacks para gráficos
@app.callback(
    Output('grafico-risco-segmento', 'figure'),
    [Input('filtro-segmento', 'value'),
     Input('filtro-risco', 'value'),
     Input('filtro-segmento-cliente', 'value'),
     Input('filtro-dias-atraso', 'value')]
)
def update_risco_segmento(segmento, risco, segmento_cliente, dias_atraso_range):
    # Garantir que os valores são listas
    segmento = segmento if isinstance(segmento, list) else [segmento]
    risco = risco if isinstance(risco, list) else [risco]
    segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
    
    filtered_df = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
    
    if len(filtered_df) == 0:
        return px.sunburst(title='Sem dados para os filtros selecionados')
    
    fig = px.sunburst(
        filtered_df, 
        path=['segmento', 'segmento_cliente'], 
        values='valor_contrato',
        title='Distribuição de Valor por Segmento e Risco',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('grafico-valor-atraso', 'figure'),
    [Input('filtro-segmento', 'value'),
     Input('filtro-risco', 'value'),
     Input('filtro-segmento-cliente', 'value'),
     Input('filtro-dias-atraso', 'value')]
)
def update_valor_atraso(segmento, risco, segmento_cliente, dias_atraso_range):
    # Garantir que os valores são listas
    segmento = segmento if isinstance(segmento, list) else [segmento]
    risco = risco if isinstance(risco, list) else [risco]
    segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
    
    filtered_df = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
    
    if len(filtered_df) == 0:
        return px.scatter(title='Sem dados para os filtros selecionados')
    
    fig = px.scatter(
        filtered_df, 
        x='dias_atraso', 
        y='valor_contrato',
        color='segmento_cliente',
        size='risco_credito',
        title='Relação: Valor vs Dias de Atraso',
        hover_data=['cliente_id']
    )
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('grafico-distribuicao-segmento', 'figure'),
    [Input('filtro-segmento', 'value'),
     Input('filtro-risco', 'value'),
     Input('filtro-segmento-cliente', 'value'),
     Input('filtro-dias-atraso', 'value')]
)
def update_distribuicao_segmento(segmento, risco, segmento_cliente, dias_atraso_range):
    # Garantir que os valores são listas
    segmento = segmento if isinstance(segmento, list) else [segmento]
    risco = risco if isinstance(risco, list) else [risco]
    segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
    
    filtered_df = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
    
    if len(filtered_df) == 0:
        return px.pie(title='Sem dados para os filtros selecionados')
    
    contagem = filtered_df['segmento_cliente'].value_counts()
    fig = px.pie(
        values=contagem.values, 
        names=contagem.index,
        title='Distribuição por Segmento de Cliente',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('grafico-satisfacao-risco', 'figure'),
    [Input('filtro-segmento', 'value'),
     Input('filtro-risco', 'value'),
     Input('filtro-segmento-cliente', 'value'),
     Input('filtro-dias-atraso', 'value')]
)
def update_satisfacao_risco(segmento, risco, segmento_cliente, dias_atraso_range):
    # Garantir que os valores são listas
    segmento = segmento if isinstance(segmento, list) else [segmento]
    risco = risco if isinstance(risco, list) else [risco]
    segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
    
    filtered_df = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
    
    if len(filtered_df) == 0:
        return px.box(title='Sem dados para os filtros selecionados')
    
    fig = px.box(
        filtered_df, 
        x='risco_credito', 
        y='satisfacao_cliente',
        title='Satisfação por Nível de Risco',
        color='risco_credito'
    )
    fig.update_layout(title_x=0.5)
    return fig

# Callbacks para exportação
@app.callback(
    Output('download-excel', 'children'),
    Input('btn-export-excel', 'n_clicks'),
    [State('filtro-segmento', 'value'),
     State('filtro-risco', 'value'),
     State('filtro-segmento-cliente', 'value'),
     State('filtro-dias-atraso', 'value')],
    prevent_initial_call=True
)
def export_excel(n_clicks, segmento, risco, segmento_cliente, dias_atraso_range):
    if n_clicks > 0:
        # Garantir que os valores são listas
        segmento = segmento if isinstance(segmento, list) else [segmento]
        risco = risco if isinstance(risco, list) else [risco]
        segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
        
        df_filtrado = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
        output = exportar_excel(df_filtrado)
        return criar_download_link(output, "clientes_credit_control.xlsx", "📥 Download Excel", "excel")
    return ""

@app.callback(
    Output('download-csv', 'children'),
    Input('btn-export-csv', 'n_clicks'),
    [State('filtro-segmento', 'value'),
     State('filtro-risco', 'value'),
     State('filtro-segmento-cliente', 'value'),
     State('filtro-dias-atraso', 'value')],
    prevent_initial_call=True
)
def export_csv(n_clicks, segmento, risco, segmento_cliente, dias_atraso_range):
    if n_clicks > 0:
        # Garantir que os valores são listas
        segmento = segmento if isinstance(segmento, list) else [segmento]
        risco = risco if isinstance(risco, list) else [risco]
        segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
        
        df_filtrado = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
        output = exportar_csv(df_filtrado)
        return criar_download_link(output, "clientes_credit_control.csv", "📥 Download CSV", "csv")
    return ""

@app.callback(
    Output('download-pdf', 'children'),
    Input('btn-export-pdf', 'n_clicks'),
    [State('filtro-segmento', 'value'),
     State('filtro-risco', 'value'),
     State('filtro-segmento-cliente', 'value'),
     State('filtro-dias-atraso', 'value')],
    prevent_initial_call=True
)
def export_pdf(n_clicks, segmento, risco, segmento_cliente, dias_atraso_range):
    if n_clicks > 0:
        # Garantir que os valores são listas
        segmento = segmento if isinstance(segmento, list) else [segmento]
        risco = risco if isinstance(risco, list) else [risco]
        segmento_cliente = segmento_cliente if isinstance(segmento_cliente, list) else [segmento_cliente]
        
        df_filtrado = get_filtered_data(segmento, risco, segmento_cliente, dias_atraso_range)
        output = exportar_pdf(df_filtrado)
        return criar_download_link(output, "clientes_credit_control.pdf", "📥 Download PDF", "pdf")
    return ""

# Callback para impressão
@app.callback(
    Output('main-container', 'children'),
    Input('btn-print', 'n_clicks'),
    prevent_initial_call=True
)
def print_report(n_clicks):
    if n_clicks and n_clicks > 0:
        return html.Script("window.print();")
    return dash.no_update

# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == '__main__':
    print("🚀 Credit Control Dashboard com Filtros Interativos")
    print("📊 Gerando dados do portfolio...")
    print(f"✅ Dados gerados: {len(df)} clientes")
    print(f"📊 Segmentos: {dict(df['segmento'].value_counts())}")
    print(f"🎯 Riscos: {dict(df['risco_credito'].value_counts().sort_index())}")
    print("🌈 Dashboard rodando em: http://0.0.0.0:8050")
    print("📤 Exportação: Excel, CSV, PDF, Impressão")
    print("🧠 Análises Dinâmicas: Ativadas e sincronizadas com filtros")
    print("🔢 Seleção Múltipla: Ativada em todos os filtros dropdown")
    
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=True
    )