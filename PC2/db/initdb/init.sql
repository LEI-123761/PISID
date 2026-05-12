SET NAMES utf8mb4;

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
    IDMongo INT,
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
    IDMongo INT,
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
    IDMongo INT,
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
  LimiarTemperatura decimal(4,2) DEFAULT 4, 
  LimiarSom decimal(4,2) DEFAULT 4,

  -- alertas (only read on mysql, can be defined by user)
  LimiarAlertaTemperatura decimal(4,2) DEFAULT 5,
  LimiarAlertaSom decimal(4,2) DEFAULT 5,

  UNIQUE KEY unique_IDSimulacao (IDSimulacao),
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
    DECLARE lastMsg TIMESTAMP;
    DECLARE currentTime TIMESTAMP;

    SELECT TemperaturaMax, TemperaturaMin, LimiarAlertaTemperatura
    INTO tempMax, tempMin, limiarTemp
    FROM Parametros
    WHERE IDSimulacao = NEW.IDSimulacao;

    /*get ultima msg time*/
    SELECT HoraEscrita
    INTO lastMsg
    FROM Mensagens
    WHERE IDSimulacao = NEW.IDSimulacao
    ORDER BY HoraEscrita DESC
    LIMIT 1;

    IF lastMsg IS NULL THEN
        SET lastMsg= '2000-01-01 00:00:00';
    END IF;

    SET currentTime= NOW();

    IF NEW.Temperatura >= (tempMax - limiarTemp) THEN
        IF TIMESTAMPDIFF(SECOND, lastMsg, currentTime) >= 3 THEN /*ultima msgs ha 3 segs ou mais?*/
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
    END IF;

    IF NEW.Temperatura <= (tempMin + limiarTemp) THEN
        IF TIMESTAMPDIFF(SECOND, lastMsg, currentTime) >= 3 THEN /*ultima msgs ha 3 segs ou mais?*/
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
    DECLARE lastMsg TIMESTAMP;
    DECLARE currentTime TIMESTAMP;

    SELECT LimiarAlertaSom
    INTO limiarSom
    FROM Parametros
    WHERE IDSimulacao = NEW.IDSimulacao;

    /*get ultima msg time*/
    SELECT HoraEscrita /*nao sei se isto da*/
    INTO lastMsg
    FROM Mensagens
    WHERE IDSimulacao = NEW.IDSimulacao
    ORDER BY HoraEscrita DESC
    LIMIT 1;

    IF lastMsg IS NULL THEN
        SET lastMsg= '2000-01-01 00:00:00';
    END IF;

    SET currentTime= NOW(); /*tb nao sei se isto da XD*/

    IF NEW.Som >= (
        SELECT SomMax FROM Parametros
        WHERE IDSimulacao = NEW.IDSimulacao
    ) - limiarSom THEN
        IF TIMESTAMPDIFF(SECOND, lastMsg, currentTime) >= 3 THEN /*ultima msgs ha 3 segs ou mais?*/
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
CREATE USER IF NOT EXISTS 'mig_som'@'%' IDENTIFIED BY 'mig_som4';
GRANT SELECT,INSERT ON maze.Som TO 'mig_som'@'%';
GRANT SELECT ON maze.Mensagens TO 'mig_som'@'%';
GRANT SELECT ON maze.Simulacao TO 'mig_som'@'%';
GRANT SELECT ON maze.Parametros TO 'mig_som'@'%';

-- Permissões temperatura script
CREATE USER IF NOT EXISTS 'mig_temperatura'@'%' IDENTIFIED BY 'mig_temperatura4';
GRANT SELECT, INSERT ON maze.Temperatura TO 'mig_temperatura'@'%';
GRANT SELECT ON maze.Mensagens TO 'mig_temperatura'@'%';
GRANT SELECT ON maze.Simulacao TO 'mig_temperatura'@'%';
GRANT SELECT ON maze.Parametros TO 'mig_temperatura'@'%';

-- Permissões movimentos script
CREATE USER IF NOT EXISTS 'mig_movimentos'@'%' IDENTIFIED BY 'mig_movimentos4';
GRANT SELECT,INSERT ON maze.MedicoesPassagens TO 'mig_movimentos'@'%';
GRANT SELECT ON maze.Simulacao TO 'mig_movimentos'@'%';

--
-- Valores iniciais:
--

-- utilizador
INSERT INTO Utilizador (Email, Nome, Telemovel, Tipo, DataNascimento, Equipa) VALUES
('Misael_Armando@iscte-iul.pt', 'Misael Armando', '912345678', 'admin', '1990-01-01', 4);

-- simulacao
INSERT INTO Simulacao (Descricao, IDUtilizador, Status)
VALUES ('Simulação de teste', 1, 'Correr');
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
VALUES (1, 35, 5, 27, 5, 5)
ON DUPLICATE KEY UPDATE IDSimulacao = IDSimulacao;

-- =========================
-- STORED PROCEDURES
-- =========================

DELIMITER $$

CREATE PROCEDURE Alterar_jogo(
    IN p_idSimulacao INT,
    IN campo_a_alterar VARCHAR(50),
    IN valor_a_alterar VARCHAR(100)
)
BEGIN
    IF campo_a_alterar = 'Descricao' THEN
        UPDATE Simulacao
        SET Descricao = valor_a_alterar
        WHERE IDSimulacao = p_idSimulacao;

    ELSEIF campo_a_alterar = 'LimiarTemperatura' THEN
        INSERT INTO Parametros (IDSimulacao, LimiarTemperatura)
        VALUES (p_idSimulacao, CAST(valor_a_alterar AS DECIMAL(4,2)))
        ON DUPLICATE KEY UPDATE LimiarTemperatura = VALUES(LimiarTemperatura);

    ELSEIF campo_a_alterar = 'LimiarAlertaTemperatura' THEN
        INSERT INTO Parametros (IDSimulacao, LimiarAlertaTemperatura)
        VALUES (p_idSimulacao, CAST(valor_a_alterar AS DECIMAL(4,2)))
        ON DUPLICATE KEY UPDATE LimiarAlertaTemperatura = VALUES(LimiarAlertaTemperatura);

    ELSEIF campo_a_alterar = 'LimiarSom' THEN
        INSERT INTO Parametros (IDSimulacao, LimiarSom)
        VALUES (p_idSimulacao, CAST(valor_a_alterar AS DECIMAL(4,2)))
        ON DUPLICATE KEY UPDATE LimiarSom = VALUES(LimiarSom);

    ELSEIF campo_a_alterar = 'LimiarAlertaSom' THEN
        INSERT INTO Parametros (IDSimulacao, LimiarAlertaSom)
        VALUES (p_idSimulacao, CAST(valor_a_alterar AS DECIMAL(4,2)))
        ON DUPLICATE KEY UPDATE LimiarAlertaSom = VALUES(LimiarAlertaSom);

    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Campo inválido';
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE Alterar_utilizador(
    IN campo_a_alterar VARCHAR(50),
    IN valor_a_alterar VARCHAR(100)
)
BEGIN

    IF campo_a_alterar = 'Nome' THEN
        UPDATE Utilizador
        SET Nome = valor_a_alterar
        WHERE Email = SUBSTRING_INDEX(USER(), '@', 2);

    ELSEIF campo_a_alterar = 'Telemovel' THEN
        UPDATE Utilizador
        SET Telemovel = valor_a_alterar
        WHERE Email = SUBSTRING_INDEX(USER(), '@', 2);

    ELSEIF campo_a_alterar = 'DataNascimento' THEN
        UPDATE Utilizador
        SET DataNascimento = STR_TO_DATE(valor_a_alterar, '%Y-%m-%d')
        WHERE Email = SUBSTRING_INDEX(USER(), '@', 2);

    ELSEIF campo_a_alterar = 'Email' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Não é permitido alterar o email';

    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Campo inválido';
    END IF;

END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE Cria_utilizador(
    IN p_email VARCHAR(50),
    IN p_nome VARCHAR(100),
    IN p_telemovel VARCHAR(12),
    IN p_tipo VARCHAR(10),
    IN p_dataNascimento DATE,
    IN p_equipa INT
)
BEGIN
    DECLARE v_username VARCHAR(50);

    -- Extrair username (parte antes do @)
    SET v_username = SUBSTRING_INDEX(p_email, '@', 1);

    -- Inserir na tabela Utilizador
    INSERT INTO Utilizador (Email, Nome, Telemovel, Tipo, DataNascimento, Equipa)
    VALUES (p_email, p_nome, p_telemovel, p_tipo, p_dataNascimento, p_equipa);

    -- Criar utilizador MySQL
    SET @sql = CONCAT(
        'CREATE USER ''', p_email, '''@''%'' IDENTIFIED BY ''', v_username, ''''
    );
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- Atribuir ROLE consoante o tipo
    IF p_tipo = 'admin' THEN

        SET @sql = CONCAT(
            'GRANT ''admin'' TO ''', p_email, '''@''%'''
        );
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        -- definir como role ativo por defeito
        SET @sql = CONCAT(
            'SET DEFAULT ROLE ''admin'' TO ''', p_email, '''@''%'''
        );
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

    ELSE

        SET @sql = CONCAT(
            'GRANT ''jogador'' TO ''', p_email, '''@''%'''
        );
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        -- definir como role ativo por defeito
        SET @sql = CONCAT(
            'SET DEFAULT ROLE ''jogador'' TO ''', p_email, '''@''%'''
        );
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

    END IF;

END$$


DELIMITER ;

DELIMITER $$

CREATE PROCEDURE Criar_jogo(
    IN p_idUtilizador INT,
    IN p_descricao TEXT,
    IN p_limiarTemperatura DECIMAL(4,2),
    IN p_limiarAlertaTemperatura DECIMAL(4,2),
    IN p_limiarSom DECIMAL(4,2),
    IN p_limiarAlertaSom DECIMAL(4,2)
)
BEGIN
    DECLARE v_idSimulacao INT;

    INSERT INTO Simulacao (Descricao, IDUtilizador, Status, DataHoraInicio)
    VALUES (p_descricao, p_idUtilizador, 'Criado', NOW());

    SET v_idSimulacao = LAST_INSERT_ID();

    INSERT INTO Parametros (
        IDSimulacao,
        LimiarTemperatura,
        LimiarAlertaTemperatura,
        LimiarSom,
        LimiarAlertaSom
    )
    VALUES (
        v_idSimulacao,
        p_limiarTemperatura,
        p_limiarAlertaTemperatura,
        p_limiarSom,
        p_limiarAlertaSom
    );
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE Remover_utilizador()
BEGIN
    DECLARE v_email VARCHAR(255);
    DECLARE v_idUtilizador INT;

    -- Extrair o email do USER()
    SET v_email = SUBSTRING_INDEX(USER(), '@', 2);

    -- Remover da tabela Utilizador
    DELETE FROM Utilizador
    WHERE Email = v_email;

    -- Extrair username MySQL (igual ao email)
    SET @fulluser := USER();
    SET @username := SUBSTRING_INDEX(@fulluser, '@', 2);

    -- Descobrir o host real do utilizador MySQL
    SELECT Host INTO @host
    FROM mysql.user
    WHERE User = @username
    LIMIT 1;

    -- Apagar utilizador MySQL se existir
    IF @host IS NOT NULL THEN
        SET @sql := CONCAT('DROP USER ''', @username, '''@''', @host, '''');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE Remover_utilizador_admin(
    IN email_a_remover VARCHAR(255)
)
BEGIN
    DECLARE host_part VARCHAR(255);

    -- Remover da tabela Utilizador
    DELETE FROM Utilizador
    WHERE Email = email_a_remover;

    -- Obter o host do utilizador MySQL
    SELECT Host INTO host_part
    FROM mysql.user
    WHERE User = email_a_remover
    LIMIT 1;

    -- Se existir, remover o utilizador MySQL
    IF host_part IS NOT NULL THEN
        SET @sql = CONCAT(
            'DROP USER ''', email_a_remover, '''@''', host_part, ''''
        );
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;

END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE Validar_login(
    IN p_email VARCHAR(255),
    IN p_password VARCHAR(255),
    OUT p_valido BOOLEAN
)
BEGIN
    DECLARE v_password_real VARCHAR(255);

    -- A password real é a parte antes do @
    SET v_password_real = SUBSTRING_INDEX(p_email, '@', 1);

    -- Comparar password fornecida com a password real
    IF p_password = v_password_real THEN
        SET p_valido = TRUE;
    ELSE
        SET p_valido = FALSE;
    END IF;
END$$

DELIMITER ;
-- ADMIN (tudo na BD)
GRANT ALL PRIVILEGES ON maze.* TO 'admin';

-- EXECUTE correto
GRANT EXECUTE ON maze.* TO 'admin';


-- JOGADOR (leitura global)
GRANT SELECT ON maze.* TO 'jogador';

-- EXECUTE por procedure (um a um!)
GRANT EXECUTE ON PROCEDURE maze.Alterar_utilizador TO 'jogador';
GRANT EXECUTE ON PROCEDURE maze.Remover_utilizador TO 'jogador';
GRANT EXECUTE ON PROCEDURE maze.Criar_jogo TO 'jogador';
GRANT EXECUTE ON PROCEDURE maze.Alterar_jogo TO 'jogador';


CALL Cria_utilizador('iappb@iscte-iul.pt', 'Iris', '123456789', 'admin', '1999-08-06', '4');
