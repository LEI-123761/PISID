<?php
session_start();
$error="";

if ($_SERVER["REQUEST_METHOD"] == "POST") {

    // Ligação à base de dados
    $ligacao = new mysqli("mysql", "root", "root", "maze");

    // Verificar erros de ligação
    if ($ligacao->connect_error) {
        die("Erro na ligação: " . $ligacao->connect_error);
    }

    // Dados do formulário
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    // Query preparada
    $sql = "CALL Validar_login(?, ?, @valido)";

    $stmt = $ligacao->prepare($sql);
    $stmt->bind_param("ss", $username, $password);
    $stmt->execute();

    $resultado = $ligacao->query("SELECT @valido AS valido");
    $row = $resultado->fetch_assoc();

    if($row['valido']){
        $sql_user = "SELECT IDUtilizador, Email FROM Utilizador WHERE Email = ?";
        $stmt_user = $ligacao->prepare($sql_user);
        $stmt_user->bind_param("s", $username);
        $stmt_user->execute();
        $res_user = $stmt_user->get_result();
        $dados_user = $res_user->fetch_assoc();

        $_SESSION['IDUtilizador'] = $dados_user['IDUtilizador'];
        $_SESSION['Email'] = $dados_user['Email'];
        $_SESSION['Logged'] = true;

        header("Location: simulacoes.php");
        exit();
    } else {
        $error = 1;
    }

    $stmt->close();
    $ligacao->close();
}
?>

<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maze Runner Login</title>
    <link rel="stylesheet" href="css/login.css">
</head>

<body>
<div class="container">
    <h2>Maze Runner</h2>
    <?php if ($error): ?>
        <div>
            Credenciais incorretas. Tente novamente.
        </div>
    <?php endif; ?>
    <form class="login-box" method="POST">
        <label for="username">Email</label>
        <input type="email" id="username" name="username" required>

        <label for="password">Password</label>
        <input type="password" id="password" name="password" required>

        <button type="submit">Log In</button>
    </form>
</div>

</body>
</html>