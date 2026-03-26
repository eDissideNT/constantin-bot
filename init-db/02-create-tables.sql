\c constructor;

CREATE TABLE IF NOT EXISTS bots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    messages_table_url TEXT,
    status VARCHAR(50) DEFAULT 'stopped',
    created_at TIMESTAMP DEFAULT NOW()
);
