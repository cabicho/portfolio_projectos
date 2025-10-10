from fastapi import FastAPI
import os
import asyncpg
import asyncio

app = FastAPI(title="Portfolio Engenharia Dados")

@app.get("/")
async def root():
    return {"message": "API Portfolio Engenharia de Dados - Online"}

@app.get("/health")
async def health():
    try:
        # Testar conexão com banco
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            conn = await asyncpg.connect(DATABASE_URL)
            await conn.close()
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "healthy", "database": "no_connection"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)