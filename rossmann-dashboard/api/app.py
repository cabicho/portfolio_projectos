from flask import Flask, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/kpis')
def get_kpis():
    kpis = {
        "total_revenue": 285982336,
        "eligible_stores": 1247,
        "model_accuracy": 89.2,
        "attention_stores": 84
    }
    return jsonify(kpis)

@app.route('/api/predictions')
def get_predictions():
    predictions = [
        {"week": 1, "revenue": 48500000},
        {"week": 2, "revenue": 47200000},
        {"week": 3, "revenue": 46800000},
        {"week": 4, "revenue": 47500000},
        {"week": 5, "revenue": 48000000},
        {"week": 6, "revenue": 47900000}
    ]
    return jsonify(predictions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
