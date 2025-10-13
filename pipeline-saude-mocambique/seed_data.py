import os
import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "db"),
    database=os.getenv("POSTGRES_DB", "saude_ocupacional"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
)
cur = conn.cursor()

# Inserir fontes oficiais
sources = [
    ("MISAU - Estatísticas de Saúde Laboral", "https://www.misau.gov.mz", "oficial", "Dados oficiais do Ministério da Saúde"),
    ("INE - Inquérito Nacional de Emprego", "https://www.ine.gov.mz", "oficial", "Dados do mercado de trabalho"),
    ("OIT - Indicadores de Trabalho Seguro", "https://www.ilo.org", "internacional", "Indicadores globais de segurança ocupacional"),
]

for s in sources:
    cur.execute("SELECT id FROM data_sources WHERE name=%s", (s[0],))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO data_sources (name, url, type, description, last_verified) VALUES (%s,%s,%s,%s,%s)",
            (s[0], s[1], s[2], s[3], datetime.utcnow())
        )

# Inserir dados simulados de risco
cur.execute("SELECT id FROM data_sources")
sources_ids = [row[0] for row in cur.fetchall()]

for sid in sources_ids:
    cur.execute(
        "INSERT INTO risk_assessment (source_id, region, indicator, risk_level) VALUES (%s,%s,%s,%s)",
        (sid, "Maputo", "Acidentes de Trabalho", "Moderado")
    )

conn.commit()
cur.close()
conn.close()
print("✅ Base de dados populada com fontes e dados simulados.")
