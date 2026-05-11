<?php
session_start();

if (!isset($_SESSION['IDUtilizador'])) {
    header("Location: login.php");
    exit();
}
$user_id = $_SESSION['IDUtilizador'];

$ligacao = new mysqli("mysql", "root", "root", "maze");

if ($ligacao->connect_error) {
    die("Erro na ligação: " . $ligacao->connect_error);
}

$warning = "";

if (isset($_GET['executar_id'])) {
    $id_para_correr = $_GET['executar_id'];

    $sql = "SELECT Status FROM Simulacao WHERE IDSimulacao = ? AND IDUtilizador = ?";
    $stmt = $ligacao->prepare($sql);
    $stmt->bind_param("ii", $id_para_correr, $user_id);
    $stmt->execute();
    $status_atual = $stmt->get_result()->fetch_assoc()['Status'];

    if ($status_atual == 'Correr') {
        $warning = "A simulação " . $id_para_correr . " já está a correr!";
    } else {
        $sql_update = "UPDATE Simulacao SET Status = 'Correr' WHERE IDSimulacao = ? AND IDUtilizador = ?";
        $stmt_up = $ligacao->prepare($sql_update);
        $stmt_up->bind_param("ii", $id_para_correr, $user_id);

        if ($stmt_up->execute()) {
            header("Location: " . $_SERVER['PHP_SELF']);
            exit();
        }
    }
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
        <h2 class="title"> Olá, <?php echo $_SESSION['Email']; ?></h2>
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
        <button title="Criar uma nova simulação" class="more" onclick="window.location.href='nova_simulacao.php'">Criar +</button>
    </div>
    <div class="table" >
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