CREATE DATABASE IF NOT EXISTS maze;
USE maze;

CREATE ROLE IF NOT EXISTS 'admin';
CREATE ROLE IF NOT EXISTS 'jogador';

-- =========================
-- UTILIZADOR
-- =========================
CREATE TABLE Utilizador (
    IDUtilizador INT AUTO_INCREMENT PRIMARY KEY,
    Email VARCHAR(50) UNIQUE,
    Nome VARCHAR(100),
    Telemovel VARCHAR(12),
    Tipo ENUM('admin', 'jogador'),
    DataNascimento DATE,
    Equipa INT
);

-- =========================
-- SIMULACAO
-- =========================
CREATE TABLE Simulacao (
    IDSimulacao INT AUTO_INCREMENT PRIMARY KEY,
    Descricao TEXT,
    IDUtilizador INT,
    Status ENUM('Criado', 'Correr', 'Terminado') NOT NULL,
    DataHoraInicio TIMESTAMP,

    FOREIGN KEY (IDUtilizador) REFERENCES Utilizador(IDUtilizador)
);

-- =========================
-- MEDICOES PASSAGENS
-- =========================
CREATE TABLE MedicoesPassagens (
    IDMedicao BIGINT AUTO_INCREMENT PRIMARY KEY,
    IDSimulacao INT,
    Hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    SalaOrigem INT,
    SalaDestino INT,
    Marsami INT,
    Status INT,

    FOREIGN KEY (IDSimulacao) REFERENCES Simulacao(IDSimulacao)
);

-- =========================
-- TEMPERATURA
-- =========================
CREATE TABLE Temperatura (
    IDTemperatura BIGINT AUTO_INCREMENT PRIMARY KEY,
    IDSimulacao INT,
    Hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Temperatura DECIMAL(5,2),

    FOREIGN KEY (IDSimulacao) REFERENCES Simulacao(IDSimulacao)
);

-- =========================
-- SOM
-- =========================
CREATE TABLE Som (
    IDSom BIGINT AUTO_INCREMENT PRIMARY KEY,
    IDSimulacao INT,
    Hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Som DECIMAL(5,2),

    FOREIGN KEY (IDSimulacao) REFERENCES Simulacao(IDSimulacao)
);

-- =========================
-- MENSAGENS
-- =========================
CREATE TABLE Mensagens (
    ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    IDSimulacao INT,
    Hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Sala INT,
    Sensor ENUM('1', '2'), -- 1 = Temperatura, 2 = Som
    Leitura DECIMAL(6,2),
    TipoAlerta VARCHAR(50),
    Msg VARCHAR(100),
    HoraEscrita TIMESTAMP,

    FOREIGN KEY (IDSimulacao) REFERENCES Simulacao(IDSimulacao)
);

-- =========================
-- OCUPACAO LABIRINTO
-- =========================
CREATE TABLE OcupacaoLabirinto (
    IDSimulacao INT,
    Sala INT,
    NumeroMarsamisOdd INT DEFAULT 0,
    NumeroMarsamisEven INT DEFAULT 0,

    PRIMARY KEY (IDSimulacao, Sala),
    FOREIGN KEY (IDSimulacao) REFERENCES Simulacao(IDSimulacao)
);
