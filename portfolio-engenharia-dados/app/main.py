from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import asyncpg
import asyncio
from datetime import datetime

app = FastAPI(title="Sistema de Relatórios Regulamentares")

# Configurar templates e arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal com dashboard"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = await asyncpg.connect(DATABASE_URL)
        
        projects_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        etl_jobs = await conn.fetch("SELECT * FROM etl_jobs ORDER BY start_time DESC LIMIT 5")
        sales_data = await conn.fetch("SELECT * FROM sales_data ORDER BY sale_date DESC LIMIT 10")
        
        await conn.close()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects_count": projects_count,
            "etl_jobs": etl_jobs,
            "sales_data": sales_data,
            "api_url": "https://portfolio-engenharia-api-42tz.onrender.com"
        })
        
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e),
            "api_url": "https://portfolio-engenharia-api-42tz.onrender.com"
        })

@app.post("/run-pipeline")
async def run_pipeline(request: Request):
    """Executar pipeline ETL"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = await asyncpg.connect(DATABASE_URL)
        
        job_id = await conn.fetchval('''
            INSERT INTO etl_jobs (job_name, status, start_time)
            VALUES ($1, $2, $3) RETURNING id
        ''', 'pipeline_manual', 'running', datetime.now())
        
        sample_data = [
            ('Laptop Dell', 'Electronics', 2, 1200.00, '2024-01-22', 'North'),
            ('Mouse Wireless', 'Electronics', 15, 45.99, '2024-01-22', 'South')
        ]
        
        for product in sample_data:
            await conn.execute('''
                INSERT INTO sales_data (product_name, category, quantity, price, sale_date, region)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', *product)
        
        await conn.execute('''
            UPDATE etl_jobs 
            SET status = $1, records_processed = $2, end_time = $3
            WHERE id = $4
        ''', 'completed', len(sample_data), datetime.now(), job_id)
        
        await conn.close()
        return RedirectResponse(url="/?message=Pipeline executado com sucesso!", status_code=303)
        
    except Exception as e:
        return RedirectResponse(url=f"/?error=Erro no pipeline: {str(e)}", status_code=303)

@app.get("/api/health")
async def health():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
