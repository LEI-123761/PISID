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
    $sql = "CALL Criar_jogo(?, ?)";
    $stmt = $ligacao->prepare($sql);
    $stmt->bind_param("is", $user_id, $nova_descricao);

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
    <h2>Nova Simulação</h2>
    <div>
        <form class="edit-box" method="POST">
            <label for="descricao">Descrição</label>
            <textarea id="descricao" name="descricao" required></textarea>
            <div class="button-container">
                <button type="button" class="cancel" onclick="window.location.href='simulacoes.php'">Cancelar</button>
                <button type="submit" name="btnGuardar">Guardar</button>
            </div>
        </form>
    </div>
</div>

</body>
</html>
