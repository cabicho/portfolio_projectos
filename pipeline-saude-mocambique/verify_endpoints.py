from fastapi import FastAPI
from datetime import datetime
import psycopg2, os, requests

app = FastAPI(title="Saúde Ocupacional - API de Verificação")

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "db"),
    "database": os.getenv("POSTGRES_DB", "saude_ocupacional"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/api/verify-sources")
def verify_sources():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, url FROM data_sources")
    results = []
    for (id, name, url) in cur.fetchall():
        try:
            response = requests.get(url, timeout=5)
            status = "ativo" if response.status_code == 200 else "inativo"
        except Exception:
            status = "inativo"
        cur.execute("UPDATE data_sources SET last_verified=%s WHERE id=%s", (datetime.utcnow(), id))
        results.append({"id": id, "fonte": name, "status": status})
    conn.commit()
    cur.close()
    conn.close()
    return {"verificacoes": results}

@app.get("/api/verify-risks")
def verify_risks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, region, indicator, risk_level FROM risk_assessment")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"avaliacoes_risco": [
        {"id": r[0], "regiao": r[1], "indicador": r[2], "nivel_risco": r[3]} for r in rows
    ]}

@app.get("/api/verify-all")
def verify_all():
    return {
        "sources": verify_sources(),
        "risks": verify_risks()
    }
