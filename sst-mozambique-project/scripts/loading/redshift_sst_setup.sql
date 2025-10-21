-- Criar schema analytics
CREATE SCHEMA IF NOT EXISTS analytics;

-- Tabela de empresas (INE)
CREATE TABLE IF NOT EXISTS analytics.stg_ine_empresas (
    id SERIAL PRIMARY KEY,
    ano INTEGER NOT NULL,
    provincia VARCHAR(100) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    total_empresas INTEGER,
    total_trabalhadores INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de acidentes (MITESS)
CREATE TABLE IF NOT EXISTS analytics.stg_mitess_acidentes (
    id SERIAL PRIMARY KEY,
    data_acidente DATE,
    provincia VARCHAR(100),
    empresa VARCHAR(200),
    tipo_acidente VARCHAR(100),
    gravidade VARCHAR(50),
    indice_gravidade INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de indicadores OIT
CREATE TABLE IF NOT EXISTS analytics.stg_ilo_indicadores (
    id SERIAL PRIMARY KEY,
    ano INTEGER,
    pais VARCHAR(10),
    indicador VARCHAR(50),
    valor DECIMAL(10,4),
    unidade_medida VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir dados de exemplo
INSERT INTO analytics.stg_ine_empresas (ano, provincia, sector, total_empresas, total_trabalhadores) VALUES
(2023, 'Maputo Cidade', 'Todos', 14800, 444000),
(2023, 'Maputo Província', 'Todos', 8000, 240000),
(2023, 'Gaza', 'Todos', 5000, 150000);

INSERT INTO analytics.stg_mitess_acidentes (data_acidente, provincia, empresa, tipo_acidente, gravidade, indice_gravidade) VALUES
('2023-01-15', 'Maputo Cidade', 'Empresa A', 'Queda', 'Moderado', 3),
('2023-02-20', 'Maputo Província', 'Empresa B', 'Corte', 'Leve', 2),
('2023-03-10', 'Gaza', 'Empresa C', 'Electrocussão', 'Grave', 4);

INSERT INTO analytics.stg_ilo_indicadores (ano, pais, indicador, valor, unidade_medida) VALUES
(2023, 'MOZ', 'INJ_TX_FREQ', 4.0, 'por 100.000 trabalhadores'),
(2023, 'MOZ', 'INJ_TX_SEV', 1.8, 'dias perdidos por acidente'),
(2023, 'MOZ', 'INJ_FATL_TX', 0.02, 'por 1.000 trabalhadores');
