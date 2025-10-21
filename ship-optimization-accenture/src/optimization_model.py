import pandas as pd
import pulp
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class ShipRouteOptimizer:
    def __init__(self, data_path='data/ships_data.csv'):
        self.df = pd.read_csv(data_path)
        self.problem = None
        self.solution = None
        self.optimization_time = None
        
    def create_optimization_model(self):
        """Cria modelo de otimização de rotas usando Pesquisa Operacional"""
        print("⚡ Criando modelo de otimização de Pesquisa Operacional...")
        
        # Inicializar problema de maximização
        self.problem = pulp.LpProblem("Otimizacao_Frota_Navios_Accenture", pulp.LpMaximize)
        
        # Variáveis de decisão binárias
        ship_vars = pulp.LpVariable.dicts(
            "SelecionarNavio", 
            self.df.index, 
            cat=pulp.LpBinary
        )
        
        # FUNÇÃO OBJETIVO: Maximizar lucro total
        self.problem += pulp.lpSum([
            self.df.loc[i, 'profit_usd'] * ship_vars[i] 
            for i in self.df.index
        ]), "Lucro_Total"
        
        # RESTRIÇÕES DE PESQUISA OPERACIONAL
        
        # 1. Restrição de capacidade máxima da frota (80% dos navios)
        max_ships = len(self.df) * 0.8
        self.problem += pulp.lpSum([ship_vars[i] for i in self.df.index]) <= max_ships, "Capacidade_Maxima_Frota"
        
        # 2. Navios em manutenção não podem operar
        maintenance_ships = self.df[self.df['maintenance_due']].index
        for ship_idx in maintenance_ships:
            self.problem += ship_vars[ship_idx] == 0, f"Manutencao_Navio_{ship_idx}"
        
        # 3. Balanceamento por tipo de navio (máximo 90% por tipo)
        ship_types = self.df['ship_type'].unique()
        for ship_type in ship_types:
            type_ships = self.df[self.df['ship_type'] == ship_type].index
            max_type_usage = len(type_ships) * 0.9
            self.problem += pulp.lpSum([ship_vars[i] for i in type_ships]) <= max_type_usage, f"Maximo_{ship_type}"
        
        # 4. Restrição de eficiência mínima (lucro > 0)
        for i in self.df.index:
            if self.df.loc[i, 'profit_usd'] <= 0:
                self.problem += ship_vars[i] == 0, f"Eficiencia_Minima_{i}"
        
        print("✅ Modelo de Pesquisa Operacional criado com sucesso!")
        print(f"   - Variáveis de decisão: {len(ship_vars)}")
        print(f"   - Restrições: {len(self.problem.constraints)}")
        
    def solve(self):
        """Resolve o modelo de otimização usando solver PuLP"""
        if self.problem is None:
            self.create_optimization_model()
            
        print("🔍 Resolvendo modelo de otimização...")
        start_time = datetime.now()
        
        # Resolver o problema
        self.problem.solve(pulp.PULP_CBC_CMD(msg=1, timeLimit=30))
        
        self.optimization_time = (datetime.now() - start_time).total_seconds()
        
        print(f"📊 Status da Otimização: {pulp.LpStatus[self.problem.status]}")
        print(f"💰 Lucro Total Otimizado: USD {pulp.value(self.problem.objective):,.2f}")
        print(f"⏱️  Tempo de execução: {self.optimization_time:.2f} segundos")
        
        # Extrair solução
        self.extract_solution()
        
    def extract_solution(self):
        """Extrai e analisa a solução ótima"""
        selected_ships = []
        for i in self.df.index:
            var_name = f"SelecionarNavio_{i}"
            if var_name in self.problem.variablesDict():
                var = self.problem.variablesDict()[var_name]
                if var.varValue == 1:
                    selected_ships.append(i)
        
        self.solution = self.df.loc[selected_ships].copy()
        
        print(f"🎯 RESULTADOS DA OTIMIZAÇÃO:")
        print(f"   - Navios selecionados: {len(self.solution)}/{len(self.df)}")
        print(f"   - Taxa de utilização da frota: {len(self.solution)/len(self.df)*100:.1f}%")
        print(f"   - Lucro médio por navio: USD {self.solution['profit_usd'].mean():,.2f}")
        print(f"   - Custo total operacional: USD {self.solution['total_cost_usd'].sum():,.2f}")
        
        print(f"🚢 Distribuição por tipo de navio:")
        type_dist = self.solution['ship_type'].value_counts()
        for ship_type, count in type_dist.items():
            print(f"     - {ship_type}: {count} navios")
        
    def generate_optimization_report(self):
        """Gera relatório completo da otimização"""
        if self.solution is None:
            print("❌ Execute a otimização primeiro!")
            return
            
        print("📈 Gerando relatório de otimização...")
        
        # Configurar estilo dos gráficos
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Comparação antes/depois da otimização
        plt.subplot(3, 4, 1)
        comparison_data = {
            'Antes': [len(self.df), self.df['profit_usd'].sum(), self.df['profit_usd'].mean()],
            'Depois': [len(self.solution), self.solution['profit_usd'].sum(), self.solution['profit_usd'].mean()]
        }
        x = np.arange(3)
        width = 0.35
        plt.bar(x - width/2, comparison_data['Antes'], width, label='Antes', alpha=0.7)
        plt.bar(x + width/2, comparison_data['Depois'], width, label='Depois', alpha=0.7)
        plt.xlabel('Métricas')
        plt.ylabel('Valores')
        plt.title('Comparação: Antes vs Depois da Otimização')
        plt.xticks(x, ['Navios', 'Lucro Total', 'Lucro Médio'])
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 2. Distribuição de lucro dos navios selecionados
        plt.subplot(3, 4, 2)
        plt.hist(self.solution['profit_usd'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(self.solution['profit_usd'].mean(), color='red', linestyle='--', label=f'Média: USD {self.solution["profit_usd"].mean():,.0f}')
        plt.xlabel('Lucro (USD)')
        plt.ylabel('Frequência')
        plt.title('Distribuição de Lucro - Navios Selecionados')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 3. Composição da frota selecionada por tipo
        plt.subplot(3, 4, 3)
        type_counts = self.solution['ship_type'].value_counts()
        plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('Composição da Frota Selecionada por Tipo')
        
        # 4. Portos mais utilizados
        plt.subplot(3, 4, 4)
        port_usage = pd.concat([self.solution['origin_port'], self.solution['destination_port']])
        port_usage.value_counts().head(8).plot(kind='bar', color='lightcoral')
        plt.title('Top 8 Portos Mais Utilizados')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # 5. Eficiência de combustível vs Lucro
        plt.subplot(3, 4, 5)
        plt.scatter(self.solution['fuel_efficiency'], self.solution['profit_usd'], alpha=0.6, c=self.solution['fuel_efficiency'], cmap='viridis')
        plt.xlabel('Eficiência de Combustível (Lucro/Consumo)')
        plt.ylabel('Lucro (USD)')
        plt.title('Relação: Eficiência vs Lucro')
        plt.colorbar(label='Eficiência')
        plt.grid(True, alpha=0.3)
        
        # 6. Capacidade vs Lucro
        plt.subplot(3, 4, 6)
        plt.scatter(self.solution['capacity_ton'], self.solution['profit_usd'], alpha=0.6, c=self.solution['travel_time_days'], cmap='plasma')
        plt.xlabel('Capacidade (toneladas)')
        plt.ylabel('Lucro (USD)')
        plt.title('Relação: Capacidade vs Lucro')
        plt.colorbar(label='Tempo de Viagem (dias)')
        plt.grid(True, alpha=0.3)
        
        # 7. Análise de custos
        plt.subplot(3, 4, 7)
        cost_components = ['fuel_cost_usd', 'port_cost_usd', 'operating_cost_usd_d']
        cost_data = self.solution[cost_components].mean()
        cost_data.plot(kind='bar', color=['#ff9999', '#66b3ff', '#99ff99'])
        plt.title('Distribuição Média de Custos')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # 8. Utilização da frota por tipo
        plt.subplot(3, 4, 8)
        utilization_by_type = self.solution.groupby('ship_type')['utilization_rate'].mean()
        utilization_by_type.plot(kind='barh', color='lightgreen')
        plt.title('Taxa de Utilização por Tipo de Navio')
        plt.xlabel('Taxa de Utilização')
        plt.grid(True, alpha=0.3)
        
        # 9. Tempo de viagem vs Distância
        plt.subplot(3, 4, 9)
        plt.scatter(self.solution['distance_nm'], self.solution['travel_time_days'], alpha=0.6, c=self.solution['profit_usd'], cmap='hot')
        plt.xlabel('Distância (milhas náuticas)')
        plt.ylabel('Tempo de Viagem (dias)')
        plt.title('Relação: Distância vs Tempo de Viagem')
        plt.colorbar(label='Lucro (USD)')
        plt.grid(True, alpha=0.3)
        
        # 10. Top 10 rotas mais lucrativas
        plt.subplot(3, 4, 10)
        routes_profit = self.solution.groupby(['origin_port', 'destination_port'])['profit_usd'].sum()
        routes_profit.nlargest(10).plot(kind='bar', color='gold')
        plt.title('Top 10 Rotas Mais Lucrativas')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # 11. Análise de velocidade vs eficiência
        plt.subplot(3, 4, 11)
        plt.scatter(self.solution['speed_knots'], self.solution['fuel_efficiency'], alpha=0.6, c=self.solution['profit_usd'], cmap='cool')
        plt.xlabel('Velocidade (nós)')
        plt.ylabel('Eficiência de Combustível')
        plt.title('Relação: Velocidade vs Eficiência')
        plt.colorbar(label='Lucro (USD)')
        plt.grid(True, alpha=0.3)
        
        # 12. Resumo estatístico
        plt.subplot(3, 4, 12)
        metrics = ['Navios Selecionados', 'Lucro Total', 'Lucro Médio', 'Custo Médio']
        values = [len(self.solution), self.solution['profit_usd'].sum()/1e6, self.solution['profit_usd'].mean()/1000, self.solution['total_cost_usd'].mean()/1000]
        bars = plt.bar(metrics, values, color=['blue', 'green', 'orange', 'red'])
        plt.title('Métricas Principais da Otimização')
        plt.xticks(rotation=45)
        plt.ylabel('Valores (USD milhões/mil)')
        
        # Adicionar valores nas barras
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{value:.1f}', 
                    ha='center', va='bottom', fontweight='bold')
        
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('data/optimization_comprehensive_report.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Salvar solução em CSV
        self.solution.to_csv('data/optimized_fleet_solution.csv', index=False)
        
        # Gerar relatório textual
        self.generate_text_report()
        
        print("✅ Relatório completo gerado em 'data/optimization_comprehensive_report.png'")
        print("💾 Solução salva em 'data/optimized_fleet_solution.csv'")
    
    def generate_text_report(self):
        """Gera relatório textual detalhado"""
        report = [
            "RELATÓRIO DE OTIMIZAÇÃO - FROTA DE NAVIOS",
            "=" * 50,
            f"Data da otimização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Tempo de execução: {self.optimization_time:.2f} segundos",
            f"Status: {pulp.LpStatus[self.problem.status]}",
            "",
            "RESUMO EXECUTIVO:",
            f"- Total de navios disponíveis: {len(self.df)}",
            f"- Navios selecionados na solução ótima: {len(self.solution)}",
            f"- Taxa de utilização da frota: {len(self.solution)/len(self.df)*100:.1f}%",
            f"- Lucro total projetado: USD {self.solution['profit_usd'].sum():,.2f}",
            f"- Lucro médio por navio: USD {self.solution['profit_usd'].mean():,.2f}",
            f"- Custo total operacional: USD {self.solution['total_cost_usd'].sum():,.2f}",
            "",
            "DISTRIBUIÇÃO POR TIPO DE NAVIO:",
        ]
        
        for ship_type in self.solution['ship_type'].value_counts().items():
            report.append(f"- {ship_type[0]}: {ship_type[1]} navios")
        
        report.extend([
            "",
            "ANÁLISE DE EFICIÊNCIA:",
            f"- Eficiência média de combustível: {self.solution['fuel_efficiency'].mean():.2f}",
            f"- Taxa média de utilização: {self.solution['utilization_rate'].mean():.1%}",
            f"- Velocidade média: {self.solution['speed_knots'].mean():.1f} nós",
            "",
            "TOP 5 ROTAS MAIS LUCRATIVAS:"
        ])
        
        top_routes = self.solution.groupby(['origin_port', 'destination_port'])['profit_usd'].sum().nlargest(5)
        for i, ((origin, dest), profit) in enumerate(top_routes.items(), 1):
            report.append(f"{i}. {origin} → {dest}: USD {profit:,.2f}")
        
        with open('data/optimization_report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

def main():
    """Função principal"""
    print("🚢 OTIMIZAÇÃO DE FROTA DE NAVIOS - ACCENTURE")
    print("=" * 60)
    
    # Verificar se os dados existem
    if not os.path.exists('data/ships_data.csv'):
        print("❌ Arquivo de dados não encontrado. Execute data/generate_data.py primeiro.")
        return
    
    # Carregar dados
    print("📊 Carregando dados da frota...")
    optimizer = ShipRouteOptimizer()
    
    print("\n📈 ANÁLISE INICIAL DA FROTA:")
    print(f"   - Total de navios: {len(optimizer.df)}")
    print(f"   - Lucro total potencial: USD {optimizer.df['profit_usd'].sum():,.2f}")
    print(f"   - Lucro médio: USD {optimizer.df['profit_usd'].mean():,.2f}")
    print(f"   - Navios em manutenção: {optimizer.df['maintenance_due'].sum()}")
    print(f"   - Tipos de navios: {', '.join(optimizer.df['ship_type'].unique())}")
    
    # Executar otimização
    print("\n" + "="*60)
    optimizer.solve()
    
    # Gerar relatórios
    print("\n" + "="*60)
    optimizer.generate_optimization_report()
    
    print("\n✅ OTIMIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("📁 Verifique os arquivos gerados na pasta /data/")

if __name__ == "__main__":
    main()
