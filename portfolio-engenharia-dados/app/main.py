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

async def get_db_connection():
    """Obter conexão com o banco"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada")
    return await asyncpg.connect(DATABASE_URL)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal com dashboard"""
    try:
        conn = await get_db_connection()
        
        # Buscar dados com tratamento de erro
        try:
            projects_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        except:
            projects_count = 0
            
        try:
            etl_jobs = await conn.fetch("SELECT * FROM etl_jobs ORDER BY start_time DESC LIMIT 5")
        except:
            etl_jobs = []
            
        try:
            sales_data = await conn.fetch("SELECT * FROM sales_data ORDER BY sale_date DESC LIMIT 10")
        except:
            sales_data = []
        
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
            "error": f"Erro de conexão: {str(e)}",
            "projects_count": 0,
            "etl_jobs": [],
            "sales_data": [],
            "api_url": "https://portfolio-engenharia-api-42tz.onrender.com"
        })

@app.post("/run-pipeline")
async def run_pipeline(request: Request):
    """Executar pipeline ETL"""
    try:
        conn = await get_db_connection()
        
        # Verificar se a tabela sales_data existe, se não, criar
        try:
            await conn.execute("SELECT 1 FROM sales_data LIMIT 1")
        except:
            # Criar tabela se não existir
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS sales_data (
                    id SERIAL PRIMARY KEY,
                    product_name VARCHAR(100),
                    category VARCHAR(50),
                    quantity INTEGER,
                    price DECIMAL(10,2),
                    sale_date DATE,
                    region VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
        
        # Registrar job
        job_id = await conn.fetchval('''
            INSERT INTO etl_jobs (job_name, status, start_time)
            VALUES ($1, $2, $3) RETURNING id
        ''', 'pipeline_manual', 'running', datetime.now())
        
        # Dados de exemplo
        sample_data = [
            ('Laptop Dell', 'Electronics', 2, 1200.00, '2024-01-22', 'North'),
            ('Mouse Wireless', 'Electronics', 15, 45.99, '2024-01-22', 'South'),
            ('Notebook', 'Office', 25, 4.99, '2024-01-21', 'East'),
            ('Pen Set', 'Office', 40, 12.99, '2024-01-21', 'West'),
            ('Monitor 24"', 'Electronics', 3, 299.99, '2024-01-22', 'North')
        ]
        
        # Inserir dados
        for product in sample_data:
            await conn.execute('''
                INSERT INTO sales_data (product_name, category, quantity, price, sale_date, region)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', *product)
        
        # Finalizar job
        await conn.execute('''
            UPDATE etl_jobs 
            SET status = $1, records_processed = $2, end_time = $3
            WHERE id = $4
        ''', 'completed', len(sample_data), datetime.now(), job_id)
        
        await conn.close()
        
        return RedirectResponse(url="/?message=Pipeline executado com sucesso! 5 registros processados.", status_code=303)
        
    except Exception as e:
        return RedirectResponse(url=f"/?error=Erro no pipeline: {str(e)}", status_code=303)

@app.get("/list-reports")
async def list_reports(request: Request):
    """Listar relatórios disponíveis"""
    try:
        conn = await get_db_connection()
        
        # Buscar métricas para relatórios
        total_projects = await conn.fetchval("SELECT COUNT(*) FROM projects")
        total_etl_jobs = await conn.fetchval("SELECT COUNT(*) FROM etl_jobs")
        total_sales = await conn.fetchval("SELECT COUNT(*) FROM sales_data")
        total_revenue = await conn.fetchval("SELECT SUM(price * quantity) FROM sales_data") or 0
        
        await conn.close()
        
        return templates.TemplateResponse("reports.html", {
            "request": request,
            "total_projects": total_projects,
            "total_etl_jobs": total_etl_jobs,
            "total_sales": total_sales,
            "total_revenue": float(total_revenue),
            "api_url": "https://portfolio-engenharia-api-42tz.onrender.com"
        })
        
    except Exception as e:
        return RedirectResponse(url=f"/?error=Erro ao gerar relatórios: {str(e)}", status_code=303)

@app.get("/api/health")
async def health():
    """Endpoint de saúde da API"""
    try:
        conn = await get_db_connection()
        
        # Testar todas as tabelas
        tables = ['projects', 'etl_jobs', 'sales_data']
        table_status = {}
        
        for table in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                table_status[table] = {"exists": True, "count": count}
            except:
                table_status[table] = {"exists": False, "count": 0}
        
        await conn.close()
        
        return {
            "status": "healthy", 
            "database": "connected",
            "tables": table_status
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
