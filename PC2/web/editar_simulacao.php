<?php
session_start();
if (!isset($_SESSION['IDUtilizador'])) {
    header("Location: login.php");
    exit();
}

$user_id = $_SESSION['IDUtilizador'];
$simulacao_id = $_GET['id'];

$ligacao = new mysqli("mysql", "root", "root", "maze");

$sql = "SELECT * FROM Simulacao WHERE IDSimulacao = ? AND IDUtilizador = ?";
$stmt = $ligacao->prepare($sql);
$stmt->bind_param("ii", $simulacao_id, $user_id);
$stmt->execute();
$dados = $stmt->get_result()->fetch_assoc();

if (!$dados) {
    die("Simulação não encontrada ou sem permissão.");
}

if ($dados['Status'] === 'Correr') {
    header("Location: simulacoes.php?erro=bloqueado&id=" . $simulacao_id);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['btnGuardar'])) {
    $nova_descricao = $_POST['descricao'];
    $sql = "CALL Alterar_jogo(?, ?)";
    $stmt = $ligacao->prepare($sql);
    $stmt->bind_param("is", $simulacao_id, $nova_descricao);

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
    <title>Editar Simulação</title>
    <link rel="stylesheet" href="css/editar_simulacao.css">
</head>

<body>
<div class="container">
    <h2>Editar Simulação <?php echo $dados['IDSimulacao']; ?></h2>
    <div>
        <form class="edit-box" method="POST">
            <label for="descricao">Descrição</label>
            <textarea id="descricao" name="descricao" required><?php echo $dados['Descricao']; ?></textarea>
            <div class="button-container">
                <button type="button" class="cancel" onclick="window.location.href='simulacoes.php'">Cancelar</button>
                <button type="submit" name="btnGuardar">Guardar</button>
            </div>
        </form>
    </div>
</div>

</body>
</html>
