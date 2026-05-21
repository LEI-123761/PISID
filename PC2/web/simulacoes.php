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

$warning = "";
$warning3 = "";

if (isset($_GET['executar_id'])) {
    $sql_check = "SELECT COUNT(*) as total FROM Simulacao WHERE Status = 'Correr'";
    $stmt_check = $ligacao->prepare($sql_check);
    $stmt_check->execute();
    $res_check = $stmt_check->get_result();
    $row_check = $res_check->fetch_assoc();

    if ($row_check['total'] > 0) {
        $warning3 = "Já existe uma simulação em execução!";
    } else {
        $id_para_correr = $_GET['executar_id'];

        $sql_update = "UPDATE Simulacao SET Status = 'Correr' WHERE IDSimulacao = ? AND IDUtilizador = ?";
        $stmt_up = $ligacao->prepare($sql_update);
        $stmt_up->bind_param("ii", $id_para_correr, $user_id);

        if ($stmt_up->execute()) {
            header("Location: " . $_SERVER['PHP_SELF']);
        }

        # COMANDO PARA CORRER O JOGO!!!!!!
//        file_get_contents("http://host.docker.internal:5000/run?id=$id_para_correr");

        $ch = curl_init("http://host.docker.internal:5000/run?id=$id_para_correr");
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 1);
        curl_exec($ch);
        curl_close($ch);
    }
}

$warning2 = "";

if (isset($_GET['erro']) && $_GET['erro'] == 'bloqueado') {
    $id_erro = isset($_GET['id']) ? $_GET['id'] : "";
    $warning2 = "Não é possível editar a simulação $id_erro. (Já está em execução)";
}

$sql = "SELECT IDSimulacao, Descricao, Status FROM Simulacao WHERE IDUtilizador = ?";
$stmt=$ligacao->prepare($sql);
$stmt->bind_param("i", $user_id);
$stmt->execute();
$resultado = $stmt->get_result();
?>

<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulações</title>
    <link rel="stylesheet" href="css/simulacoes.css">
</head>

<body>
<div class="container">
    <div class="header-container">
        <h2 class="title"> Olá, <a href="perfil.php" title="Editar perfil" class="user-link"><?php echo $_SESSION['Email']; ?></a></h2>
        <?php if ($warning != ""): ?>
            <div id="popup-warning" class="alert">
                <?php echo $warning; ?>
            </div>

            <script>
                var popup = document.getElementById('popup-warning');

                if (popup) {
                    setTimeout(function() {
                        popup.classList.add('show');
                    }, 100);

                    setTimeout(function() {
                        popup.classList.remove('show');

                        setTimeout(function() {
                            popup.remove();
                        }, 500);
                    }, 2500);
                }
            </script>
        <?php endif; ?>
        <?php if ($warning2 != ""): ?>
            <div id="popup-warning" class="alert">
                <?php echo $warning2; ?>
            </div>

            <script>
                var popup = document.getElementById('popup-warning');

                if (popup) {
                    setTimeout(function() {
                        popup.classList.add('show');
                    }, 100);

                    setTimeout(function() {
                        popup.classList.remove('show');

                        setTimeout(function() {
                            popup.remove();
                        }, 500);
                    }, 2500);
                }
            </script>
        <?php endif; ?>
        <?php if ($warning3 != ""): ?>
            <div id="popup-warning" class="alert">
                <?php echo $warning3; ?>
            </div>

            <script>
                var popup = document.getElementById('popup-warning');

                if (popup) {
                    setTimeout(function() {
                        popup.classList.add('show');
                    }, 100);

                    setTimeout(function() {
                        popup.classList.remove('show');

                        setTimeout(function() {
                            popup.remove();
                        }, 500);
                    }, 2500);
                }
            </script>
        <?php endif; ?>

        <button title="Criar uma nova simulação" class="more" onclick="window.location.href='nova_simulacao.php'">Criar +</button>
    </div>
    <div class="table">
        <table>
            <tr>
                <th>ID</th>
                <th>Descrição</th>
                <th>Estado</th>
                <th>Ações</th>
            </tr>
            <tbody>
            <?php if ($resultado->num_rows > 0): ?>
                <?php while($row = $resultado->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo $row['IDSimulacao']; ?></td>
                        <td><?php echo $row['Descricao']; ?></td>
                        <td><?php echo $row['Status']; ?></td>
                        <td class="acoes-container">
                            <button title="Editar" class="btn-edit" onclick="window.location.href='editar_simulacao.php?id=<?php echo $row['IDSimulacao']; ?>'">✎</button>
                            <button title="Correr" class="btn-play" onclick="window.location.href='?executar_id=<?php echo $row['IDSimulacao']; ?>'">▶</button>
                            <button title="Mais informações" class="btn-info" onclick="window.location.href='simulacao.php?id=<?php echo $row['IDSimulacao']; ?>'">ⓘ</button>
                        </td>
                    </tr>
                <?php endwhile; ?>
            <?php else: ?>
                <tr>
                    <td colspan="4">Ainda não tens nenhuma simulação criada.</td>
                </tr>
            <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>


</body>
</html>

<?php
$stmt->close();
$ligacao->close();
?>