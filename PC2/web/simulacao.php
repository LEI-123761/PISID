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

if ($ligacao->connect_error) {
    die("Erro na ligação: " . $ligacao->connect_error);
}

$sql = "SELECT * FROM Simulacao WHERE IDSimulacao = ? AND IDUtilizador = ?";
$stmt = $ligacao->prepare($sql);
$stmt->bind_param("ii", $simulacao_id, $user_id);
$stmt->execute();
$dados = $stmt->get_result()->fetch_assoc();

if (!$dados) {
    die("Simulação não encontrada ou sem permissão.");
}

?>

<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detalhes Simulação</title>
    <link rel="stylesheet" href="css/perfil.css">
</head>

<body>
<div class="container">
    <h2 class="title">Detalhes Simulação <?php echo $simulacao_id ?>:</h2>
    <form method="POST" >
        <div class="form-compact">
            <div class="form-grid">
                <div class="input-group">
                    <label for="limTemp">Limiar Temperatura</label>
                    <input id="limTemp" name="limTemp">
                </div>
                <div class="input-group">
                    <label for="limSom">Limiar Som</label>
                    <input id="limSom" name="limSom">
                </div>
                <div class="input-group">
                    <label for="limAlertTemp">Limiar Alerta Temperatura</label>
                    <input id="limAlertTemp" name="limAlertTemp">
                </div>
                <div class="input-group">
                    <label for="limAlertSom">Limiar Alerta Som</label>
                    <input id="limAlertSom" name="limAlertSom">
                </div>
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
