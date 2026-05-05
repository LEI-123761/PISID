<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

$response = array('success' => false, 'message' => '', 'data' => null);

$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

$host = 'mysql'; // No Docker use o nome do serviço

$conn = new mysqli($host, $username, $password, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de ligação: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

$sql = "SELECT TemperaturaMax as maximo, TemperaturaMin as minimo FROM Parametros LIMIT 1";
$result = $conn->query($sql);

if ($result && $row = $result->fetch_assoc()) {
    $response['success'] = true;
    $response['data'] = array(
        "minimo" => (float)$row['minimo'],
        "maximo" => (float)$row['maximo']
    );
} else {
    $response['message'] = "Não foram encontrados limites na tabela.";
}

$conn->close();
echo json_encode($response);