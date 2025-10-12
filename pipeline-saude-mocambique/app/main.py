import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    from src.api.dashboard import app
    
    uvicorn.run(
        "src.api.dashboard:app",
        host=host,
        port=port,
        reload=False
    )
