import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def perform_comprehensive_eda():
    """Realiza análise exploratória completa dos dados"""
    print("🔍 ANÁLISE EXPLORATÓRIA COMPLETA - DADOS DE NAVIOS")
    print("=" * 60)
    
    # Carregar dados
    df = pd.read_csv('data/ships_data.csv')
    
    print(f"📊 Dataset: {len(df)} registros, {len(df.columns)} variáveis")
    
    # Estatísticas descritivas
    print("\n📈 ESTATÍSTICAS DESCRITIVAS:")
    print(df.describe())
    
    # Análise por tipo de navio
    print("\n🚢 ANÁLISE POR TIPO DE NAVIO:")
    type_analysis = df.groupby('ship_type').agg({
        'profit_usd': ['count', 'mean', 'sum', 'std'],
        'total_cost_usd': 'mean',
        'capacity_ton': 'mean',
        'speed_knots': 'mean',
        'fuel_efficiency': 'mean'
    }).round(2)
    print(type_analysis)
    
    # Configurar visualizações
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(25, 20))
    
    # 1. Distribuição de lucros
    plt.subplot(4, 5, 1)
    plt.hist(df['profit_usd'], bins=30, alpha=0.7, color='blue', edgecolor='black')
    plt.axvline(df['profit_usd'].mean(), color='red', linestyle='--', label=f'Média: USD {df["profit_usd"].mean():,.0f}')
    plt.xlabel('Lucro (USD)')
    plt.ylabel('Frequência')
    plt.title('Distribuição de Lucros da Frota')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. Boxplot de lucro por tipo de navio
    plt.subplot(4, 5, 2)
    df.boxplot(column='profit_usd', by='ship_type', ax=plt.gca())
    plt.title('Distribuição de Lucro por Tipo de Navio')
    plt.suptitle('')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 3. Matriz de correlação
    plt.subplot(4, 5, 3)
    numeric_cols = ['capacity_ton', 'speed_knots', 'distance_nm', 'travel_time_days', 
                   'fuel_consumption_td', 'profit_usd', 'fuel_efficiency']
    corr_matrix = df[numeric_cols].corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0, 
                square=True, fmt='.2f', cbar_kws={"shrink": .8})
    plt.title('Matriz de Correlação (Triangular)')
    
    # 4. Portos mais lucrativos (origem)
    plt.subplot(4, 5, 4)
    port_profit = df.groupby('origin_port')['profit_usd'].mean().sort_values(ascending=False)
    port_profit.head(8).plot(kind='bar', color='lightgreen')
    plt.title('Portos de Origem Mais Lucrativos')
    plt.xticks(rotation=45)
    plt.ylabel('Lucro Médio (USD)')
    plt.grid(True, alpha=0.3)
    
    # 5. Relação custo vs lucro
    plt.subplot(4, 5, 5)
    plt.scatter(df['total_cost_usd'], df['profit_usd'], alpha=0.6, c=df['fuel_efficiency'], cmap='viridis')
    plt.xlabel('Custo Total (USD)')
    plt.ylabel('Lucro (USD)')
    plt.title('Relação: Custo Total vs Lucro')
    plt.colorbar(label='Eficiência Combustível')
    plt.grid(True, alpha=0.3)
    
    # 6. Distribuição de capacidade
    plt.subplot(4, 5, 6)
    plt.hist(df['capacity_ton'], bins=25, alpha=0.7, color='orange', edgecolor='black')
    plt.axvline(df['capacity_ton'].mean(), color='red', linestyle='--', label=f'Média: {df["capacity_ton"].mean():,.0f} ton')
    plt.xlabel('Capacidade (toneladas)')
    plt.ylabel('Frequência')
    plt.title('Distribuição de Capacidade da Frota')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 7. Eficiência por tipo de navio
    plt.subplot(4, 5, 7)
    df.boxplot(column='fuel_efficiency', by='ship_type', ax=plt.gca())
    plt.title('Eficiência de Combustível por Tipo de Navio')
    plt.suptitle('')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 8. Top 10 rotas mais lucrativas
    plt.subplot(4, 5, 8)
    routes_profit = df.groupby(['origin_port', 'destination_port'])['profit_usd'].mean()
    routes_profit.nlargest(10).plot(kind='bar', color='lightcoral')
    plt.title('Top 10 Rotas Mais Lucrativas (Lucro Médio)')
    plt.xticks(rotation=45)
    plt.ylabel('Lucro Médio (USD)')
    plt.grid(True, alpha=0.3)
    
    # 9. Tempo de viagem vs Distância
    plt.subplot(4, 5, 9)
    plt.scatter(df['distance_nm'], df['travel_time_days'], alpha=0.6, c=df['speed_knots'], cmap='plasma')
    plt.xlabel('Distância (milhas náuticas)')
    plt.ylabel('Tempo de Viagem (dias)')
    plt.title('Relação: Distância vs Tempo de Viagem')
    plt.colorbar(label='Velocidade (nós)')
    plt.grid(True, alpha=0.3)
    
    # 10. Análise de velocidade
    plt.subplot(4, 5, 10)
    plt.hist(df['speed_knots'], bins=20, alpha=0.7, color='purple', edgecolor='black')
    plt.axvline(df['speed_knots'].mean(), color='red', linestyle='--', label=f'Média: {df["speed_knots"].mean():.1f} nós')
    plt.xlabel('Velocidade (nós)')
    plt.ylabel('Frequência')
    plt.title('Distribuição de Velocidade da Frota')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 11. Consumo de combustível vs Lucro
    plt.subplot(4, 5, 11)
    plt.scatter(df['fuel_consumption_td'], df['profit_usd'], alpha=0.6, c=df['travel_time_days'], cmap='cool')
    plt.xlabel('Consumo de Combustível (t/dia)')
    plt.ylabel('Lucro (USD)')
    plt.title('Relação: Consumo vs Lucro')
    plt.colorbar(label='Tempo Viagem (dias)')
    plt.grid(True, alpha=0.3)
    
    # 12. Análise de custos operacionais
    plt.subplot(4, 5, 12)
    cost_components = ['fuel_cost_usd', 'port_cost_usd', 'operating_cost_usd_d']
    cost_data = df[cost_components].mean()
    cost_data.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
    plt.title('Distribuição Média de Custos')
    plt.ylabel('')
    
    # 13. Navios que precisam de manutenção
    plt.subplot(4, 5, 13)
    maintenance_counts = df['maintenance_due'].value_counts()
    maintenance_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, labels=['Operacional', 'Manutenção'], colors=['lightblue', 'lightcoral'])
    plt.title('Status de Manutenção da Frota')
    plt.ylabel('')
    
    # 14. Taxa de utilização
    plt.subplot(4, 5, 14)
    plt.hist(df['utilization_rate'], bins=20, alpha=0.7, color='teal', edgecolor='black')
    plt.axvline(df['utilization_rate'].mean(), color='red', linestyle='--', label=f'Média: {df["utilization_rate"].mean():.1%}')
    plt.xlabel('Taxa de Utilização')
    plt.ylabel('Frequência')
    plt.title('Distribuição da Taxa de Utilização')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 15. Análise de distâncias
    plt.subplot(4, 5, 15)
    plt.hist(df['distance_nm'], bins=25, alpha=0.7, color='brown', edgecolor='black')
    plt.axvline(df['distance_nm'].mean(), color='red', linestyle='--', label=f'Média: {df["distance_nm"].mean():,.0f} nm')
    plt.xlabel('Distância (milhas náuticas)')
    plt.ylabel('Frequência')
    plt.title('Distribuição de Distâncias das Rotas')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 16. Correlação lucro vs eficiência
    plt.subplot(4, 5, 16)
    plt.scatter(df['fuel_efficiency'], df['profit_usd'], alpha=0.6, c=df['capacity_ton'], cmap='hot')
    plt.xlabel('Eficiência de Combustível')
    plt.ylabel('Lucro (USD)')
    plt.title('Relação: Eficiência vs Lucro')
    plt.colorbar(label='Capacidade (ton)')
    plt.grid(True, alpha=0.3)
    
    # 17. Análise por porto de destino
    plt.subplot(4, 5, 17)
    dest_profit = df.groupby('destination_port')['profit_usd'].mean().sort_values(ascending=False)
    dest_profit.head(8).plot(kind='bar', color='lightseagreen')
    plt.title('Portos de Destino Mais Lucrativos')
    plt.xticks(rotation=45)
    plt.ylabel('Lucro Médio (USD)')
    plt.grid(True, alpha=0.3)
    
    # 18. Tempo total de operação
    plt.subplot(4, 5, 18)
    plt.hist(df['total_time_days'], bins=20, alpha=0.7, color='navy', edgecolor='black')
    plt.axvline(df['total_time_days'].mean(), color='red', linestyle='--', label=f'Média: {df["total_time_days"].mean():.1f} dias')
    plt.xlabel('Tempo Total (dias)')
    plt.ylabel('Frequência')
    plt.title('Distribuição do Tempo Total de Operação')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 19. Comparação receita vs custo
    plt.subplot(4, 5, 19)
    comparison = pd.DataFrame({
        'Receita': df['revenue_usd'].mean(),
        'Custo Total': df['total_cost_usd'].mean(),
        'Lucro': df['profit_usd'].mean()
    }, index=['Média'])
    comparison.plot(kind='bar', ax=plt.gca(), color=['green', 'red', 'blue'])
    plt.title('Comparação Média: Receita vs Custo vs Lucro')
    plt.xticks(rotation=0)
    plt.ylabel('USD')
    plt.grid(True, alpha=0.3)
    
    # 20. Resumo estatístico visual
    plt.subplot(4, 5, 20)
    metrics = ['Lucro Total', 'Custo Total', 'Receita Total', 'Navios']
    values = [df['profit_usd'].sum()/1e6, df['total_cost_usd'].sum()/1e6, df['revenue_usd'].sum()/1e6, len(df)]
    bars = plt.bar(metrics, values, color=['blue', 'red', 'green', 'purple'])
    plt.title('Métricas Gerais da Frota (Milhões USD)')
    plt.ylabel('Milhões de USD / Quantidade')
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{value:.1f}', 
                ha='center', va='bottom', fontweight='bold')
    
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/comprehensive_eda_report.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Análise estatística adicional
    print("\n📊 ANÁLISE ESTATÍSTICA AVANÇADA:")
    print(f"   - Correlação capacidade-lucro: {df['capacity_ton'].corr(df['profit_usd']):.3f}")
    print(f"   - Correlação distância-lucro: {df['distance_nm'].corr(df['profit_usd']):.3f}")
    print(f"   - Correlação eficiência-lucro: {df['fuel_efficiency'].corr(df['profit_usd']):.3f}")
    print(f"   - Tipo mais lucrativo: {df.groupby('ship_type')['profit_usd'].mean().idxmax()}")
    print(f"   - Porto mais lucrativo (origem): {df.groupby('origin_port')['profit_usd'].mean().idxmax()}")
    print(f"   - Rota mais lucrativa: {df.groupby(['origin_port', 'destination_port'])['profit_usd'].mean().idxmax()}")
    
    # Teste de normalidade do lucro
    stat, p_value = stats.normaltest(df['profit_usd'])
    print(f"   - Normalidade do lucro (p-value): {p_value:.4f}")
    
    # Salvar análise em arquivo
    with open('data/eda_insights.txt', 'w') as f:
        f.write("INSIGHTS DA ANÁLISE EXPLORATÓRIA\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total de navios analisados: {len(df)}\n")
        f.write(f"Lucro total potencial: USD {df['profit_usd'].sum():,.2f}\n")
        f.write(f"Lucro médio por navio: USD {df['profit_usd'].mean():,.2f}\n")
        f.write(f"Navios em manutenção: {df['maintenance_due'].sum()}\n\n")
        
        f.write("TOP 3 TIPOS MAIS LUCRATIVOS:\n")
        top_types = df.groupby('ship_type')['profit_usd'].mean().nlargest(3)
        for tipo, lucro in top_types.items():
            f.write(f"  - {tipo}: USD {lucro:,.2f}\n")
        
        f.write("\nTOP 3 PORTOS MAIS LUCRATIVOS:\n")
        top_ports = df.groupby('origin_port')['profit_usd'].mean().nlargest(3)
        for porto, lucro in top_ports.items():
            f.write(f"  - {porto}: USD {lucro:,.2f}\n")
    
    print(f"\n✅ Análise exploratória concluída!")
    print(f"📊 Relatório salvo em: data/comprehensive_eda_report.png")
    print(f"📋 Insights salvos em: data/eda_insights.txt")

if __name__ == "__main__":
    perform_comprehensive_eda()
