-- �������� ���� ������ �� ���������, ����� �������� ������ ��� ����������� init.sql

-- �������� ������� ������������� (���� ����� �� ������� ��������)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ������ ������� �������� �������������
INSERT INTO users (username, email, password_hash) VALUES 
('admin', 'admin@example.com', 'admin123hashed'),
('support_agent', 'agent@example.com', 'agent123hashed'),
('test_user', 'user@example.com', 'user123hashed')
ON CONFLICT DO NOTHING;

-- �������� ������� �������� (tickets)
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE tickets ADD COLUMN is_in_trello BOOLEAN DEFAULT FALSE;


-- �������� ������������ ��������� ���� ������
SELECT 'Schema successfully created!' AS status_message;
