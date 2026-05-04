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
    Status ENUM('Criado', 'Correr', 'Terminado') NOT NULL DEFAULT 'Criado',
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
    Sensor ENUM('TEMP', 'SOM'), -- TEMP = Temperatura, SOM = Som
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

CREATE TABLE Parametros (
  IDParametros int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  IDSimulacao int(11) DEFAULT NULL,
  -- User does not set these values, they are updated by the system based on the readings
  TemperaturaMax decimal(4,2) DEFAULT NULL,
  TemperaturaMin decimal(4,2) DEFAULT NULL,
  SomMax decimal(4,2) DEFAULT NULL,

  -- outliers (only read on mongo)
  LimiarTemperatura decimal(4,2) DEFAULT 5, 
  LimiarSom decimal(4,2) DEFAULT 5,

  -- alertas (only read on mysql, can be defined by user)
  LimiarAlertaTemperatura decimal(4,2) DEFAULT 5,
  LimiarAlertaSom decimal(4,2) DEFAULT 5,

  FOREIGN KEY (IDSimulacao) REFERENCES Simulacao(IDSimulacao)
);

--
-- Acionadores `Temperatura`
--
DELIMITER $$
CREATE TRIGGER Trg_alerta_temp AFTER INSERT ON Temperatura FOR EACH ROW BEGIN
    DECLARE tempMax DECIMAL(4,2);
    DECLARE tempMin DECIMAL(4,2);
    DECLARE limiarTemp DECIMAL(4,2);

    SELECT TemperaturaMax, TemperaturaMin, LimiarAlertaTemperatura
    INTO tempMax, tempMin, limiarTemp
    FROM Parametros
    WHERE IDSimulacao = NEW.IDSimulacao;

    IF NEW.Temperatura >= (tempMax - limiarTemp) THEN
        INSERT INTO Mensagens (
            IDSimulacao, Hora, Sala, Sensor, Leitura,
            TipoAlerta, Msg, HoraEscrita
        )
        VALUES (
            NEW.IDSimulacao, NEW.Hora, NULL, 'TEMP',
            NEW.Temperatura, 'ALERTA de Temperatura',
            'Temperatura próxima do limite máximo',
            NOW()
        );
    END IF;

    IF NEW.Temperatura <= (tempMin + limiarTemp) THEN
        INSERT INTO Mensagens (
            IDSimulacao, Hora, Sala, Sensor, Leitura,
            TipoAlerta, Msg, HoraEscrita
        )
        VALUES (
            NEW.IDSimulacao, NEW.Hora, NULL, 'TEMP',
            NEW.Temperatura, 'ALERTA de Temperatura',
            'Temperatura próxima do limite mínimo',
            NOW()
        );
    END IF;
END
$$
DELIMITER ;

--
-- Acionadores `Som`
--
DELIMITER $$
CREATE TRIGGER Trg_alerta_ruido AFTER INSERT ON Som FOR EACH ROW BEGIN
    DECLARE limiarSom DECIMAL(4,2);

    SELECT LimiarAlertaSom
    INTO limiarSom
    FROM Parametros
    WHERE IDSimulacao = NEW.IDSimulacao;

    IF NEW.Som >= (
        SELECT SomMax FROM Parametros
        WHERE IDSimulacao = NEW.IDSimulacao
    ) - limiarSom THEN

        INSERT INTO Mensagens (
            IDSimulacao, Hora, Sala, Sensor, Leitura,
            TipoAlerta, Msg, HoraEscrita
        )
        VALUES (
            NEW.IDSimulacao, NOW(), NULL, 'SOM',
            NEW.Som, 'ALERTA de Som',
            'Som próximo do limite máximo',
            NOW()
        );
    END IF;

END
$$
DELIMITER ;

--
-- Acionadores `OcupacaoLabirinto`
--
DROP TRIGGER IF EXISTS Trg_ocupacao_labirinto;

DELIMITER $$

CREATE TRIGGER Trg_ocupacao_labirinto
    AFTER INSERT ON MedicoesPassagens
    FOR EACH ROW
BEGIN

    -- =========================
    -- REMOVER da origem
    -- =========================
    IF NEW.SalaOrigem IS NOT NULL THEN

        IF MOD(NEW.Marsami, 2) = 0 THEN
            INSERT INTO OcupacaoLabirinto (IDSimulacao, Sala, NumeroMarsamisEven)
            VALUES (NEW.IDSimulacao, NEW.SalaOrigem, -1)
            ON DUPLICATE KEY UPDATE
                                        NumeroMarsamisEven = NumeroMarsamisEven - 1;
    ELSE
            INSERT INTO OcupacaoLabirinto (IDSimulacao, Sala, NumeroMarsamisOdd)
            VALUES (NEW.IDSimulacao, NEW.SalaOrigem, -1)
            ON DUPLICATE KEY UPDATE
                                     NumeroMarsamisOdd = NumeroMarsamisOdd - 1;
END IF;

END IF;

    -- =========================
    -- ADICIONAR ao destino
    -- =========================
    IF MOD(NEW.Marsami, 2) = 0 THEN
        INSERT INTO OcupacaoLabirinto (IDSimulacao, Sala, NumeroMarsamisEven)
        VALUES (NEW.IDSimulacao, NEW.SalaDestino, 1)
        ON DUPLICATE KEY UPDATE
                                    NumeroMarsamisEven = NumeroMarsamisEven + 1;
ELSE
        INSERT INTO OcupacaoLabirinto (IDSimulacao, Sala, NumeroMarsamisOdd)
        VALUES (NEW.IDSimulacao, NEW.SalaDestino, 1)
        ON DUPLICATE KEY UPDATE
                             NumeroMarsamisOdd = NumeroMarsamisOdd + 1;
END IF;

END$$

DELIMITER ;


--
-- Permissões
--

-- Permissões som script
CREATE USER IF NOT EXISTS 'som_user'@'%' IDENTIFIED BY 'som_password';
GRANT ALL PRIVILEGES ON maze.Som TO 'som_user'@'%';
GRANT Select ON maze.Simulacao TO 'som_user'@'%';

-- Permissões temperatura script
CREATE USER IF NOT EXISTS 'temperatura_user'@'%' IDENTIFIED BY 'temperatura_password';
GRANT ALL PRIVILEGES ON maze.Temperatura TO 'temperatura_user'@'%';
GRANT Select ON maze.Simulacao TO 'temperatura_user'@'%';

-- Permissões movimentos script
CREATE USER IF NOT EXISTS 'movimentos_user'@'%' IDENTIFIED BY 'movimentos_password';
GRANT ALL PRIVILEGES ON maze.MedicoesPassagens TO 'movimentos_user'@'%';
GRANT Select ON maze.Simulacao TO 'movimentos_user'@'%';

--
-- Valores iniciais
--

-- utilizador
INSERT INTO Utilizador (Email, Nome, Telemovel, Tipo, DataNascimento, Equipa) VALUES
('Misael_Armando@iscte-iul.pt', 'Misael Armando', '912345678', 'admin', '1990-01-01', 4);

-- simulacao
INSERT INTO Simulacao (Descricao, IDUtilizador, Status)
VALUES ('Simulação de teste', 1, 'Criado');
    -- nao tem ON DUPLICATE KEY UPDATE na Simulacao porque: não há nenhuma chave única que provoque “duplicate key”

-- parametros
INSERT INTO Parametros (
    IDSimulacao,
    TemperaturaMax,
    TemperaturaMin,
    SomMax,
    LimiarAlertaTemperatura,
    LimiarAlertaSom
)
VALUES (1, 40, 10, 80, 5, 5)
ON DUPLICATE KEY UPDATE IDSimulacao = IDSimulacao;