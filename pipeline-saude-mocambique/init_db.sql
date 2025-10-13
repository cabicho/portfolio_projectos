CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    last_verified TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_assessment (
    id SERIAL PRIMARY KEY,
    source_id INT REFERENCES data_sources(id) ON DELETE CASCADE,
    region VARCHAR(100),
    indicator VARCHAR(100),
    risk_level VARCHAR(50),
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
