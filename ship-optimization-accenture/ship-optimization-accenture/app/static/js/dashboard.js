class ShipDashboard {
    constructor() {
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadDashboardData();
        this.setupEventListeners();
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard-data');
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }

            this.updateMetrics(data.metrics);
            this.createCharts(data);
            this.updateLastUpdate(data.last_update);
            
        } catch (error) {
            this.showError('Erro ao carregar dados: ' + error.message);
        }
    }

    updateMetrics(metrics) {
        document.getElementById('total-ships').textContent = metrics.total_ships.toLocaleString();
        document.getElementById('optimized-ships').textContent = metrics.optimized_ships.toLocaleString();
        document.getElementById('utilization-rate').textContent = metrics.utilization_rate + '%';
        document.getElementById('profit-improvement').textContent = metrics.profit_improvement + '%';
    }

    createCharts(data) {
        this.createProfitByTypeChart(data.ship_types);
        this.createCostDistributionChart(data.cost_distribution);
    }

    createProfitByTypeChart(shipTypes) {
        const ctx = document.getElementById('profitByTypeChart').getContext('2d');
        
        if (this.charts.profitByType) {
            this.charts.profitByType.destroy();
        }

        this.charts.profitByType = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: shipTypes.map(st => st.type),
                datasets: [{
                    label: 'Lucro Total (Milhões USD)',
                    data: shipTypes.map(st => st.total_profit / 1000000),
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Lucro Total por Tipo de Navio'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Milhões USD'
                        }
                    }
                }
            }
        });
    }

    createCostDistributionChart(costDistribution) {
        const ctx = document.getElementById('costDistributionChart').getContext('2d');
        
        if (this.charts.costDistribution) {
            this.charts.costDistribution.destroy();
        }

        this.charts.costDistribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Combustível', 'Porto', 'Operacional'],
                datasets: [{
                    data: [
                        costDistribution.fuel,
                        costDistribution.port,
                        costDistribution.operating
                    ],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Distribuição Média de Custos'
                    }
                }
            }
        });
    }

    updateLastUpdate(timestamp) {
        document.getElementById('last-update').textContent = timestamp;
    }

    showError(message) {
        console.error('Dashboard Error:', message);
        alert('Erro: ' + message);
    }

    setupEventListeners() {
        setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new ShipDashboard();
});
