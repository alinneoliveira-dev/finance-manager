CREATE DATABASE expense_control;
USE expense_control;

CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    tipo ENUM('entrada','saida') NOT NULL,
    cor VARCHAR(20) DEFAULT '#3B82F6'
);

CREATE TABLE transacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    tipo ENUM('entrada','saida') NOT NULL,
    categoria_id INT,
    data_transacao DATE NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE limites_categoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT NOT NULL UNIQUE,
    limite_mensal DECIMAL(10,2) NOT NULL,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);
