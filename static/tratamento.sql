CREATE DATABASE IF NOT EXISTS tratamento_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE tratamento_db;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    nome VARCHAR(255),
    senha VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON tratamento_db.* TO 'Samuel'@'localhost';
FLUSH PRIVILEGES;

GRANT ALL PRIVILEGES ON tratamento_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;