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

async def ensure_tables_exist():
    """Garante que todas as tabelas existam"""
    try:
        conn = await get_db_connection()
        
        # Criar sales_data se não existir
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS sales_data (
                id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                sale_date DATE NOT NULL,
                region VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        # Criar outras tabelas se não existirem
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                technology_stack TEXT[],
                github_url VARCHAR(300),
                live_demo_url VARCHAR(300),
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS etl_jobs (
                id SERIAL PRIMARY KEY,
                job_name VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                records_processed INTEGER,
                start_time TIMESTAMP DEFAULT NOW(),
                end_time TIMESTAMP,
                error_message TEXT
            )
        ''')
        
        await conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Erro ao garantir tabelas: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Garantir que tabelas existam na inicialização"""
    print("🔧 Verificando tabelas do banco de dados...")
    await ensure_tables_exist()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal com dashboard"""
    try:
        await ensure_tables_exist()
        conn = await get_db_connection()
        
        # Buscar dados
        projects_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        etl_jobs = await conn.fetch("SELECT * FROM etl_jobs ORDER BY start_time DESC LIMIT 5")
        sales_count = await conn.fetchval("SELECT COUNT(*) FROM sales_data")
        total_revenue = await conn.fetchval("SELECT SUM(price * quantity) FROM sales_data") or 0
        
        # Buscar últimas vendas
        recent_sales = await conn.fetch("SELECT * FROM sales_data ORDER BY sale_date DESC, id DESC LIMIT 5")
        
        await conn.close()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "projects_count": projects_count,
            "etl_jobs": etl_jobs,
            "sales_count": sales_count,
            "total_revenue": float(total_revenue),
            "recent_sales": recent_sales,
            "api_url": "https://portfolio-engenharia-api-42tz.onrender.com"
        })
        
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Erro: {str(e)}",
            "projects_count": 0,
            "etl_jobs": [],
            "sales_count": 0,
            "total_revenue": 0,
            "recent_sales": [],
            "api_url": "https://portfolio-engenharia-api-42tz.onrender.com"
        })

@app.post("/run-pipeline")
async def run_pipeline(request: Request):
    """Executar pipeline ETL"""
    try:
        await ensure_tables_exist()
        conn = await get_db_connection()
        
        # Registrar job
        job_id = await conn.fetchval('''
            INSERT INTO etl_jobs (job_name, status, start_time)
            VALUES ($1, $2, $3) RETURNING id
        ''', 'pipeline_manual', 'running', datetime.now())
        
        # Dados de exemplo para ETL
        sample_data = [
            ('Laptop Gaming', 'Electronics', 1, 1999.99, '2024-10-10', 'North'),
            ('Wireless Mouse', 'Electronics', 10, 35.99, '2024-10-10', 'South'),
            ('Office Chair', 'Furniture', 2, 299.99, '2024-10-10', 'East'),
            ('Desk Lamp', 'Furniture', 5, 45.50, '2024-10-09', 'West'),
            ('Notebook Pack', 'Office', 20, 8.99, '2024-10-09', 'North')
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
        
        return RedirectResponse(url="/?message=✅ Pipeline executado com sucesso! 5 novos registros adicionados.", status_code=303)
        
    except Exception as e:
        return RedirectResponse(url=f"/?error=❌ Erro no pipeline: {str(e)}", status_code=303)

@app.get("/list-reports")
async def list_reports(request: Request):
    """Listar relatórios disponíveis"""
    try:
        await ensure_tables_exist()
        conn = await get_db_connection()
        
        # Buscar métricas para relatórios
        total_projects = await conn.fetchval("SELECT COUNT(*) FROM projects")
        total_etl_jobs = await conn.fetchval("SELECT COUNT(*) FROM etl_jobs")
        total_sales = await conn.fetchval("SELECT COUNT(*) FROM sales_data")
        total_revenue = await conn.fetchval("SELECT SUM(price * quantity) FROM sales_data") or 0
        
        # Métricas por categoria
        sales_by_category = await conn.fetch('''
            SELECT category, SUM(quantity) as total_quantity, SUM(price * quantity) as total_revenue
            FROM sales_data 
            GROUP BY category
        ''')
        
        await conn.close()
        
        return templates.TemplateResponse("reports.html", {
            "request": request,
            "total_projects": total_projects,
            "total_etl_jobs": total_etl_jobs,
            "total_sales": total_sales,
            "total_revenue": float(total_revenue),
            "sales_by_category": sales_by_category,
            "api_url": "https://portfolio-engenharia-api-42tz.onrender.com"
        })
        
    except Exception as e:
        return RedirectResponse(url=f"/?error=Erro ao gerar relatórios: {str(e)}", status_code=303)

@app.get("/force-init-db")
async def force_init_db():
    """Forçar inicialização do banco de dados"""
    try:
        # Executar script de força
        import subprocess
        result = subprocess.run([
            "python", "scripts/force_init_tables.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return {"message": "✅ Banco de dados forçadamente inicializado!", "output": result.stdout}
        else:
            return {"error": "❌ Falha na inicialização", "output": result.stderr}
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}

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
            except Exception as e:
                table_status[table] = {"exists": False, "count": 0, "error": str(e)}
        
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
