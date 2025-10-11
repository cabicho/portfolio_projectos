-- Script de inicialização do banco de dados
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de dados da OMS
CREATE TABLE IF NOT EXISTS who_data (
    id SERIAL PRIMARY KEY,
    indicador VARCHAR(255) NOT NULL,
    ano INTEGER NOT NULL,
    valor DECIMAL,
    categoria VARCHAR(100),
    fonte VARCHAR(100) DEFAULT 'OMS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(indicador, ano, categoria)
);

-- Tabela de doenças ocupacionais
CREATE TABLE IF NOT EXISTS occupational_diseases (
    id SERIAL PRIMARY KEY,
    ano INTEGER NOT NULL,
    doencas_respiratorias INTEGER DEFAULT 0,
    lesoes_musculoesqueleticas INTEGER DEFAULT 0,
    perda_auditiva INTEGER DEFAULT 0,
    doencas_pele INTEGER DEFAULT 0,
    intoxicacoes_quimicas INTEGER DEFAULT 0,
    setor_agricultura INTEGER DEFAULT 0,
    setor_construcao INTEGER DEFAULT 0,
    setor_industria INTEGER DEFAULT 0,
    setor_minas INTEGER DEFAULT 0,
    fonte VARCHAR(100) DEFAULT 'INS Moçambique',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ano)
);

-- Tabela de avaliação de risco
CREATE TABLE IF NOT EXISTS risk_assessment (
    id SERIAL PRIMARY KEY,
    provincia VARCHAR(100) NOT NULL,
    score_risco DECIMAL(5,2),
    nivel_risco VARCHAR(50),
    populacao_exposta INTEGER,
    principal_exposicao VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provincia)
);

-- Tabela de logs do pipeline
CREATE TABLE IF NOT EXISTS pipeline_logs (
    id SERIAL PRIMARY KEY,
    execution_id UUID DEFAULT uuid_generate_v4(),
    step_name VARCHAR(100),
    status VARCHAR(50),
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration INTERVAL
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_who_data_ano ON who_data(ano);
CREATE INDEX IF NOT EXISTS idx_occupational_diseases_ano ON occupational_diseases(ano);
CREATE INDEX IF NOT EXISTS idx_risk_assessment_provincia ON risk_assessment(provincia);
CREATE INDEX IF NOT EXISTS idx_risk_assessment_score ON risk_assessment(score_risco DESC);

-- Dados iniciais de exemplo
INSERT INTO occupational_diseases (ano, doencas_respiratorias, lesoes_musculoesqueleticas, perda_auditiva, doencas_pele, intoxicacoes_quimicas, setor_agricultura, setor_construcao, setor_industria, setor_minas)
VALUES 
(2020, 1250, 890, 340, 210, 95, 650, 420, 580, 180),
(2021, 1320, 920, 360, 230, 105, 680, 450, 610, 190),
(2022, 1400, 950, 380, 250, 115, 710, 480, 640, 200),
(2023, 1480, 980, 400, 270, 125, 740, 510, 670, 210)
ON CONFLICT (ano) DO NOTHING;

INSERT INTO risk_assessment (provincia, score_risco, nivel_risco, populacao_exposta, principal_exposicao)
VALUES 
('Maputo', 45.6, 'Médio', 125000, 'Particulas'),
('Gaza', 38.2, 'Médio', 89000, 'Particulas'),
('Inhambane', 32.1, 'Baixo', 67000, 'Particulas'),
('Sofala', 41.3, 'Médio', 95000, 'Particulas'),
('Manica', 36.7, 'Médio', 78000, 'Particulas'),
('Tete', 39.8, 'Médio', 82000, 'Particulas'),
('Zambézia', 34.5, 'Baixo', 105000, 'Particulas'),
('Nampula', 37.9, 'Médio', 115000, 'Particulas'),
('Cabo Delgado', 35.2, 'Médio', 92000, 'Particulas'),
('Niassa', 31.8, 'Baixo', 58000, 'Particulas')
ON CONFLICT (provincia) DO NOTHING;

-- Visualização para dashboard
CREATE OR REPLACE VIEW vw_risk_dashboard AS
SELECT 
    provincia,
    score_risco,
    nivel_risco,
    populacao_exposta,
    principal_exposicao,
    CASE 
        WHEN nivel_risco = 'Alto' THEN '🔴'
        WHEN nivel_risco = 'Médio' THEN '🟡'
        ELSE '🟢'
    END as risco_emoji
FROM risk_assessment
ORDER BY score_risco DESC;

-- Função para estatísticas
CREATE OR REPLACE FUNCTION get_risk_statistics()
RETURNS TABLE(
    total_provincias BIGINT,
    media_risco DECIMAL,
    max_risco DECIMAL,
    min_risco DECIMAL,
    total_populacao BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_provincias,
        AVG(score_risco) as media_risco,
        MAX(score_risco) as max_risco,
        MIN(score_risco) as min_risco,
        SUM(populacao_exposta) as total_populacao
    FROM risk_assessment;
END;
$$ LANGUAGE plpgsql;

