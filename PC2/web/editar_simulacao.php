<?php
session_start();
if (!isset($_SESSION['IDUtilizador'])) {
    header("Location: login.php");
    exit();
}

$simulacao_id = $_GET['id'];
$user_id = $_SESSION['IDUtilizador'];
$username = $_SESSION['Email'];
$password = $_SESSION['Password'];

$ligacao = new mysqli("mysql", $username, $password, "maze");

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

$sql2 = "SELECT LimiarTemperatura, LimiarSom, LimiarAlertaTemperatura, LimiarAlertaSom FROM Parametros WHERE IDSimulacao = ?";
$stmt2 = $ligacao->prepare($sql2);
$stmt2->bind_param("i", $simulacao_id);
$stmt2->execute();
$dados2 = $stmt2->get_result()->fetch_assoc();

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if(!empty($_POST['Descricao'])){
        $campo='Descricao';
        $stmt = $ligacao->prepare("CALL Alterar_jogo(?, ?, ?)");
        $stmt->bind_param("iss", $simulacao_id,  $campo, $_POST['Descricao']);
        if ($stmt->execute()) {
            $stmt->close();
        } else {
            $error = "Erro ao executar procedure: " . $ligacao->error;
        }
    }

    if(!empty($_POST['LimiarTemperatura'])){
        $campo='LimiarTemperatura';
        $stmt = $ligacao->prepare("CALL Alterar_jogo(?, ?, ?)");
        $stmt->bind_param("iss", $simulacao_id,$campo, $_POST['LimiarTemperatura']);
        if ($stmt->execute()) {
            $stmt->close();
        } else {
            $error = "Erro ao executar procedure: " . $ligacao->error;
        }
    }

    if(!empty($_POST['LimiarSom'])){
        $campo='LimiarSom';
        $stmt = $ligacao->prepare("CALL Alterar_jogo(?, ?, ?)");
        $stmt->bind_param("iss", $simulacao_id,$campo, $_POST['LimiarSom']);
        if ($stmt->execute()) {
            $stmt->close();
        } else {
            $error = "Erro ao executar procedure: " . $ligacao->error;
        }
    }

    if(!empty($_POST['LimiarAlertaTemperatura'])){
        $campo='LimiarAlertaTemperatura';
        $stmt = $ligacao->prepare("CALL Alterar_jogo(?, ?, ?)");
        $stmt->bind_param("iss", $simulacao_id, $campo, $_POST['LimiarAlertaTemperatura']);
        if ($stmt->execute()) {
            $stmt->close();
        } else {
            $error = "Erro ao executar procedure: " . $ligacao->error;
        }
    }

    if(!empty($_POST['LimiarAlertaSom'])){
        $campo='LimiarAlertaSom';
        $stmt = $ligacao->prepare("CALL Alterar_jogo(?, ?, ?)");
        $stmt->bind_param("iss", $simulacao_id, $campo, $_POST['LimiarAlertaSom']);
        if ($stmt->execute()) {
            $stmt->close();
        } else {
            $error = "Erro ao executar procedure: " . $ligacao->error;
        }
    }

    header("Location: simulacoes.php");
    exit();
}
?>

<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Simulação <?php echo $simulacao_id ?></title>
    <link rel="stylesheet" href="css/nova_simulacao.css">
</head>


<body>
<div class="container">
    <div class="header-container">
        <h2 class="title">Editar Simulação <?php echo $simulacao_id ?>:</h2>
    </div>
    <form class="edit-box" method="POST">
        <div class="form-grid">
            <div class="input-group-desc">
                <label for="Descricao">Descrição</label>
                <input type="text" id="Descricao" name="Descricao" value="<?php echo htmlspecialchars($dados['Descricao']); ?>">
            </div>
            <div class="input-group">
                <label for="LimiarTemperatura">Limiar Temperatura</label>
                <input type="number" id="LimiarTemperatura" name="LimiarTemperatura" step="0.01" min="0.00" value="<?php echo $dados2['LimiarTemperatura']; ?>">
            </div>

            <div class="input-group">
                <label for="LimiarAlertaTemperatura">Limiar Alerta Temperatura</label>
                <input type="number" id="LimiarAlertaTemperatura" name="LimiarAlertaTemperatura" step="0.01" min="0.00" value="<?php echo $dados2['LimiarAlertaTemperatura']; ?>">
            </div>

            <div class="input-group">
                <label for="LimiarSom">Limiar Som</label>
                <input type="number" id="LimiarSom" name="LimiarSom" step="0.01" min="0.00" value="<?php echo $dados2['LimiarSom']; ?>">
            </div>

            <div class="input-group">
                <label for="LimiarAlertaSom">Limiar Alerta Som</label>
                <input type="number" id="LimiarAlertaSom" name="LimiarAlertaSom" step="0.01" min="0.00" value="<?php echo $dados2['LimiarAlertaSom']; ?>" required>
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
