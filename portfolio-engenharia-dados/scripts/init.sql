-- init.sql
CREATE TABLE IF NOT EXISTS clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    segment VARCHAR(50),
    created_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    client_id INT,
    transaction_value DECIMAL(15,2),
    transaction_date DATE,
    risk_category VARCHAR(20),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE IF NOT EXISTS compliance_status (
    compliance_id SERIAL PRIMARY KEY,
    client_id INT,
    compliance_status VARCHAR(50),
    last_review_date DATE,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

-- Dados de exemplo
INSERT INTO clients (name, segment) VALUES 
('Empresa A', 'Corporate'),
('Empresa B', 'SME'),
('Empresa C', 'Retail'),
('Empresa D', 'Corporate'),
('Empresa E', 'SME');

INSERT INTO transactions (client_id, transaction_value, transaction_date, risk_category) VALUES 
(1, 15000.00, '2024-01-15', 'Baixo'),
(2, 8500.50, '2024-01-16', 'Médio'),
(3, 250000.00, '2024-01-17', 'Alto'),
(4, 12000.00, '2024-01-18', 'Baixo'),
(5, 95000.00, '2024-01-19', 'Alto');

INSERT INTO compliance_status (client_id, compliance_status, last_review_date) VALUES 
(1, 'Compliant', '2024-01-10'),
(2, 'Pending', '2024-01-12'),
(3, 'Non-Compliant', '2024-01-14'),
(4, 'Compliant', '2024-01-11'),
(5, 'Pending', '2024-01-13');
