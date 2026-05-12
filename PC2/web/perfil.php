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

if ($ligacao->connect_error) {
    die("Erro na ligação: " . $ligacao->connect_error);
}

$sql = "SELECT Nome, Telemovel, DataNascimento FROM Utilizador WHERE IDUtilizador = ?";
$stmt = $ligacao->prepare($sql);
$stmt->bind_param("i", $user_id);
$stmt->execute();
$resultado = $stmt->get_result();
$dados_atuais = $resultado->fetch_assoc();

$nome = $dados_atuais['Nome'] ?? "";
$tel = $dados_atuais['Telemovel'] ?? "";
$data = $dados_atuais['DataNascimento'] ?? "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (!empty($_POST['Nome'])) {
        $campo1='Nome';
        $stmt = $ligacao->prepare("CALL Alterar_utilizador(?, ?)");
        $stmt->bind_param("ss", $campo1, $_POST['Nome']);
        $stmt->execute();
        $stmt->close();
    }

    if (!empty($_POST['Telemovel'])) {
        $campo2='Telemovel';
        $stmt = $ligacao->prepare("CALL Alterar_utilizador(?, ?)");
        $stmt->bind_param("ss", $campo2, $_POST['Telemovel']);
        $stmt->execute();
        $stmt->close();
    }

    if (!empty($_POST['DataNascimento'])) {
        $campo3='DataNascimento';
        $stmt = $ligacao->prepare("CALL Alterar_utilizador(?, ?)");
        $stmt->bind_param("ss", $campo3, $_POST['DataNascimento']);
        $stmt->execute();
        $stmt->close();
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
    <title>Editar Perfil</title>
    <link rel="stylesheet" href="css/perfil.css">
</head>

<body>
<div class="container">
    <div class="header-container">
        <h2 class="title">Editar Perfil:</h2>
    </div>
    <form method="POST" >
        <div class="form-compact">
            <div class="form-grid">
                <div class="input-group">
                    <label for="Nome">Nome</label>
                    <input id="Nome" name="Nome" value="<?php echo htmlspecialchars($nome);?>">
                </div>
                <div class="input-group">
                    <label for="Telemovel">Telemóvel</label>
                    <input type="tel" id="Telemovel" name="Telemovel" value="<?php echo htmlspecialchars($tel); ?>">
                </div>
                <div class="input-group">
                    <label for="DataNascimento">Data de Nascimento</label>
                    <input type="date" id="DataNascimento" name="DataNascimento" value="<?php echo $data; ?>">
                </div>
                <div class="delete-section">
                    <button type="button" class="btn-delete">Apagar Conta</button>
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
