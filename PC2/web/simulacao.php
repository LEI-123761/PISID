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

$sql = "SELECT LimiarTemperatura, LimiarSom, LimiarAlertaTemperatura, LimiarAlertaSom FROM Parametros WHERE IDSimulacao = ?";
$stmt=$ligacao->prepare($sql);
$stmt->bind_param("i", $simulacao_id);
$stmt->execute();
$resultado = $stmt->get_result();

if (!$resultado) {
    die("Simulação não encontrada ou sem permissão.");
}

$row = $resultado->fetch_assoc();

?>

<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detalhes da Simulação <?php echo $simulacao_id ?></title>
    <link rel="stylesheet" href="css/simulacao.css">
</head>

<body>
<div class="container">
    <div class="header-container">
        <h2 class="title">Detalhes da Simulação <?php echo $simulacao_id ?>:</h2>
    </div>
    <div class="table">
        <table>
            <tr>
                <th>Limiar Temperatura</th>
                <th>Limiar Som</th>
                <th>Limiar Alerta Temperatura</th>
                <th>Limiar Alerta Som</th>
            </tr>
            <tbody>
                <tr>
                    <td><?php echo $row['LimiarTemperatura']; ?></td>
                    <td><?php echo $row['LimiarSom']; ?></td>
                    <td><?php echo $row['LimiarAlertaTemperatura']; ?></td>
                    <td><?php echo $row['LimiarAlertaSom']; ?></td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="button-container">
        <button type="button" class="" onclick="window.location.href='simulacoes.php'">Voltar</button>
    </div>
</div>

</body>
</html>
