-- Users table для аутентификации
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(500) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Clients table (из CSV)
CREATE TABLE IF NOT EXISTS clients (
    client_id VARCHAR(50) PRIMARY KEY,
    dt DATE,
    age INTEGER,
    gender VARCHAR(20),
    city VARCHAR(255),
    region VARCHAR(255),
    income_real FLOAT,  -- Реальный доход (target)
    income_predicted FLOAT,
    confidence FLOAT,
    income_category VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions (результаты прогнозов)
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id VARCHAR(50) PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL REFERENCES clients(client_id),
    user_id INTEGER REFERENCES users(user_id),
    predicted_income FLOAT NOT NULL,
    actual_income FLOAT,
    confidence FLOAT NOT NULL,
    category VARCHAR(20) NOT NULL,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id VARCHAR(50) PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL REFERENCES clients(client_id),
    prediction_id VARCHAR(50) REFERENCES predictions(prediction_id),
    product VARCHAR(100) NOT NULL,
    amount FLOAT,
    rate FLOAT,
    reason TEXT,
    was_accepted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model metrics (для монитроинга качества)
CREATE TABLE IF NOT EXISTS model_metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_date DATE,
    metric_name VARCHAR(100),
    metric_value FLOAT,
    model_version VARCHAR(50),
    dataset_type VARCHAR(20),  -- 'train', 'test'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_clients_dt ON clients(dt);
CREATE INDEX idx_clients_city ON clients(city);
CREATE INDEX idx_predictions_client_id ON predictions(client_id);
CREATE INDEX idx_predictions_user_id ON predictions(user_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
CREATE INDEX idx_model_metrics_date ON model_metrics(metric_date);

-- Тестовый юзер
INSERT INTO users (email, password_hash, full_name) 
VALUES ('demo@alfabank.ru', '$2b$12$abcd1234567890', 'Demo User')
ON CONFLICT DO NOTHING;

INSERT INTO model_metrics (metric_date, metric_name, metric_value, model_version, dataset_type)
VALUES 
    (CURRENT_DATE, 'WMAE', 0.1234, '1.0.0', 'train'),
    (CURRENT_DATE, 'WMAE', 0.1456, '1.0.0', 'test'),
    (CURRENT_DATE, 'MAE', 5234.50, '1.0.0', 'train'),
    (CURRENT_DATE, 'MAE', 6123.75, '1.0.0', 'test')
ON CONFLICT DO NOTHING;
