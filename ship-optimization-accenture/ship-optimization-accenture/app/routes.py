from flask import Blueprint, render_template, jsonify, send_file
import pandas as pd
import json
import os
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/analysis')
def analysis():
    return render_template('analysis.html')

@main.route('/optimization')
def optimization():
    return render_template('optimization.html')

@main.route('/api/dashboard-data')
def dashboard_data():
    try:
        ships_df = pd.read_csv('data/ships_data.csv')
        optimized_df = pd.read_csv('data/optimized_fleet_solution.csv')
        
        total_ships = len(ships_df)
        optimized_ships = len(optimized_df)
        utilization_rate = (optimized_ships / total_ships) * 100
        
        total_profit = ships_df['profit_usd'].sum()
        optimized_profit = optimized_df['profit_usd'].sum()
        profit_improvement = ((optimized_profit / total_profit) - 1) * 100
        
        ship_type_analysis = ships_df.groupby('ship_type').agg({
            'profit_usd': ['count', 'sum', 'mean'],
            'fuel_efficiency': 'mean'
        }).round(2)
        
        ship_type_data = []
        for ship_type in ship_type_analysis.index:
            ship_type_data.append({
                'type': ship_type,
                'count': int(ship_type_analysis.loc[ship_type, ('profit_usd', 'count')]),
                'total_profit': float(ship_type_analysis.loc[ship_type, ('profit_usd', 'sum')]),
                'avg_profit': float(ship_type_analysis.loc[ship_type, ('profit_usd', 'mean')]),
                'efficiency': float(ship_type_analysis.loc[ship_type, ('fuel_efficiency', 'mean')])
            })
        
        port_analysis_origin = ships_df.groupby('origin_port')['profit_usd'].sum().nlargest(10)
        top_ports_origin = [{'port': port, 'profit': float(profit)} 
                           for port, profit in port_analysis_origin.items()]
        
        cost_distribution = {
            'fuel': float(ships_df['fuel_cost_usd'].mean()),
            'port': float(ships_df['port_cost_usd'].mean()),
            'operating': float(ships_df['operating_cost_usd_d'].mean() * ships_df['total_time_days'].mean())
        }
        
        return jsonify({
            'metrics': {
                'total_ships': total_ships,
                'optimized_ships': optimized_ships,
                'utilization_rate': round(utilization_rate, 1),
                'total_profit': float(total_profit),
                'optimized_profit': float(optimized_profit),
                'profit_improvement': round(profit_improvement, 1),
                'avg_profit_per_ship': float(ships_df['profit_usd'].mean()),
                'avg_optimized_profit': float(optimized_df['profit_usd'].mean())
            },
            'ship_types': ship_type_data,
            'top_ports_origin': top_ports_origin,
            'cost_distribution': cost_distribution,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/optimization-results')
def optimization_results():
    try:
        optimized_df = pd.read_csv('data/optimized_fleet_solution.csv')
        
        optimization_metrics = {
            'total_selected': len(optimized_df),
            'total_profit': float(optimized_df['profit_usd'].sum()),
            'avg_profit': float(optimized_df['profit_usd'].mean()),
            'total_cost': float(optimized_df['total_cost_usd'].sum()),
            'total_revenue': float(optimized_df['revenue_usd'].sum()),
            'avg_efficiency': float(optimized_df['fuel_efficiency'].mean()),
            'avg_utilization': float(optimized_df['utilization_rate'].mean()) * 100
        }
        
        type_distribution = optimized_df['ship_type'].value_counts().to_dict()
        
        top_routes = optimized_df.groupby(['origin_port', 'destination_port'])['profit_usd'].sum().nlargest(10)
        top_routes_data = [{'route': f"{origin} → {dest}", 'profit': float(profit)} 
                          for (origin, dest), profit in top_routes.items()]
        
        return jsonify({
            'optimization_metrics': optimization_metrics,
            'type_distribution': type_distribution,
            'top_routes': top_routes_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/reports/<report_name>')
def download_report(report_name):
    safe_path = os.path.join('data', report_name)
    if os.path.exists(safe_path):
        return send_file(safe_path, as_attachment=True)
    return jsonify({'error': 'Relatório não encontrado'}), 404
