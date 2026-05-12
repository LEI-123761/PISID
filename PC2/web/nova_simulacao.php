<?php
session_start();
if (!isset($_SESSION['IDUtilizador'])) {
    header("Location: login.php");
    exit();
}

$user_id = $_SESSION['IDUtilizador'];
$username = $_SESSION['Email'];
$password = $_SESSION['Password'];

$ligacao = new mysqli("mysql", $username, $password, "maze");

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['btnGuardar'])) {
    $nova_descricao = $_POST['descricao'];
    $limTemp = $_POST['limTemp'];
    $limAlertTemp = $_POST['limAlertTemp'];
    $limSom = $_POST['limSom'];
    $limAlertSom = $_POST['limAlertSom'];

    $sql = "CALL Criar_jogo(?, ?, ?, ?, ?)";
    $stmt = $ligacao->prepare($sql);
    $stmt->bind_param("siiii", $nova_descricao, $limTemp, $limAlertTemp, $limSom, $limAlertSom);

    if ($stmt->execute()) {
        $stmt->close();
        $ligacao->close();
        header("Location: simulacoes.php");
        exit();
    } else {
        $error = "Erro ao executar procedure: " . $ligacao->error;
    }
}
?>

<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova Simulação</title>
    <link rel="stylesheet" href="css/nova_simulacao.css">
</head>

<body>
<div class="container">
    <div class="header-container">
        <h2 class="title">Nova Simulação</h2>
    </div>
    <form class="edit-box" method="POST">
        <div class="form-grid">
            <div class="input-group-desc">
                <label for="descricao">Descrição</label>
                <input type="text" id="descricao" name="descricao" required>
            </div>

            <div class="input-group">
                <label for="limTemp">Limiar Temperatura</label>
                <input type="number" id="limTemp" name="limTemp" step="0.01" min="0.00" value="4.00" required>
            </div>

            <div class="input-group">
                <label for="limAlertTemp">Limiar Alerta Temperatura</label>
                <input type="number" id="limAlertTemp" name="limAlertTemp" step="0.01" min="0.00" value="5.00" required>
            </div>

            <div class="input-group">
                <label for="limSom">Limiar Som</label>
                <input type="number" id="limSom" name="limSom" step="0.01" min="0.00" value="4.00" required>
            </div>

            <div class="input-group">
                <label for="limAlertSom">Limiar Alerta Som</label>
                <input type="number" id="limAlertSom" name="limAlertSom" step="0.01" min="0.00" value="5.00" required>
            </div>
        </div>
        <div class="button-container">
            <button type="button" class="cancel" onclick="window.location.href='simulacoes.php'">Cancelar</button>
            <button type="submit" class="save" name="btnGuardar">Guardar</button>
        </div>
    </form>

</div>

</body>
</html>
