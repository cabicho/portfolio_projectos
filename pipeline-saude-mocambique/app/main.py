import os
import sys

# Adicionar o diretório src ao path do Python
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    from src.api.dashboard import app
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False
    )
