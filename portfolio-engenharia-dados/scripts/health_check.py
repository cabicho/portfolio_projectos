#!/usr/bin/env python3
"""
health_check.py
Verifica a saúde da API e conexão com o banco
"""

import requests
import os
import sys

def check_api_health():
    """Check if API is healthy"""
    api_url = os.getenv("RENDER_API_URL", "https://portfolio-engenharia-api.onrender.com")
    
    try:
        print(f"🔍 Verificando saúde da API: {api_url}")
        
        response = requests.get(f"{api_url}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API Online e Saudável")
            print(f"📊 Status: {health_data.get('status', 'N/A')}")
            print(f"🗄️ Database: {health_data.get('database', {}).get('status', 'N/A')}")
            print(f"🌍 Environment: {health_data.get('environment', 'N/A')}")
            return True
        else:
            print(f"❌ API com problemas. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com API: {e}")
        return False

if __name__ == "__main__":
    success = check_api_health()
    sys.exit(0 if success else 1)
