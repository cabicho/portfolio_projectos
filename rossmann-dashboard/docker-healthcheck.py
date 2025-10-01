#!/usr/bin/env python3
"""
Health check customizado para o Dashboard Rossmann
"""

import requests
import sys

def health_check():
    try:
        response = requests.get(
            "http://localhost:8050/_dash-health-check", 
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Dashboard health check passed")
            return True
        else:
            print(f"❌ Health check failed: Status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    success = health_check()
    sys.exit(0 if success else 1)
