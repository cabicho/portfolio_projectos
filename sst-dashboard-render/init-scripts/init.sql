-- Inicialização do Banco de Dados SST Dashboard

-- Tabela de departamentos
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100),
    employee_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de colaboradores
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE,
    position VARCHAR(100),
    tenure_months INTEGER DEFAULT 0,
    salary DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de métricas mensais
CREATE TABLE IF NOT EXISTS monthly_metrics (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    month DATE NOT NULL,
    turnover_rate DECIMAL(5,4),
    overtime_hours DECIMAL(8,2),
    burnout_score DECIMAL(5,2),
    productivity DECIMAL(5,2),
    health_costs DECIMAL(12,2),
    accidents INTEGER DEFAULT 0,
    risk_score DECIMAL(5,4),
    wellbeing_investment DECIMAL(12,2),
    training_hours DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(department_id, month)
);

-- Tabela de incidentes
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    employee_id INTEGER REFERENCES employees(id),
    incident_date DATE NOT NULL,
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(20),
    description TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para previsões
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    prediction_date DATE NOT NULL,
    turnover_probability DECIMAL(5,4),
    risk_level VARCHAR(20),
    factors JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir dados iniciais
INSERT INTO departments (name, location, employee_count) VALUES 
('Agência Centro', 'Centro', 45),
('Agência Norte', 'Zona Norte', 38), 
('Agência Sul', 'Zona Sul', 52),
('Agência Leste', 'Zona Leste', 41),
('Agência Oeste', 'Zona Oeste', 36),
('Matriz', 'Sede', 120);

-- Inserir métricas iniciais
INSERT INTO monthly_metrics (department_id, month, turnover_rate, overtime_hours, burnout_score, productivity, health_costs, accidents, risk_score) 
SELECT 
    id,
    DATE '2024-01-01' + (INTERVAL '1' MONTH * generate_series(0,5)),
    ROUND((0.05 + RANDOM() * 0.2)::numeric, 4),
    ROUND((30 + RANDOM() * 30)::numeric, 2),
    ROUND((40 + RANDOM() * 40)::numeric, 2),
    ROUND((65 + RANDOM() * 20)::numeric, 2),
    ROUND((50000 + RANDOM() * 70000)::numeric, 2),
    FLOOR(RANDOM() * 3)::integer,
    ROUND((0.3 + RANDOM() * 0.5)::numeric, 4)
FROM departments, generate_series(0,5);

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_metrics_department_month ON monthly_metrics(department_id, month);
CREATE INDEX IF NOT EXISTS idx_incidents_date ON incidents(incident_date);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_date);

-- View para dashboard
CREATE OR REPLACE VIEW dashboard_view AS
SELECT 
    d.name as department_name,
    d.location,
    mm.month,
    mm.turnover_rate,
    mm.overtime_hours,
    mm.burnout_score,
    mm.productivity,
    mm.health_costs,
    mm.accidents,
    mm.risk_score,
    CASE 
        WHEN mm.risk_score > 0.7 THEN 'ALTO'
        WHEN mm.risk_score > 0.4 THEN 'MÉDIO'
        ELSE 'BAIXO'
    END as risk_level
FROM monthly_metrics mm
JOIN departments d ON mm.department_id = d.id;
