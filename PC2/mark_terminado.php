<?php
$ligacao = new mysqli("mysql", "root", "root", "maze");

$data = json_decode(file_get_contents("php://input"), true);

$id = $data["id"] ?? null;

if ($id) {
    $sql_update = "UPDATE Simulacao SET Status = 'Terminado' WHERE IDSimulacao = ?";
    $stmt_up = $ligacao->prepare($sql_update);
    $stmt_up->bind_param("i", $id_para_correr);

    if ($stmt_up->execute()) {
        header("Location: " . $_SERVER['PHP_SELF']);
    }
}
?>