<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

// Estrutura padrão para o Android não crashar
$response = array('success' => false, 'message' => '', 'data' => array());

$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos.';
    echo json_encode($response);
    exit;
}

// Configuração Docker
$host = 'mysql'; 
$db_user = $username; 
$db_pass = $password; 

// Usando mysqli para consistência
$conn = new mysqli($host, $db_user, $db_pass, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de conexão: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// Query para obter os dados de temperatura
$sql = "SELECT temperatura, idtemperatura FROM temperatura ORDER BY idtemperatura ASC";
$result = $conn->query($sql);

if ($result) {
    $tempData = array();
    while ($row = $result->fetch_assoc()) {
        $tempData[] = $row;
    }
    
    $response['success'] = true;
    $response['data'] = $tempData;
    $response['message'] = 'Dados de temperatura carregados com sucesso.';
} else {
    $response['message'] = "Erro na query: " . $conn->error;
}

$conn->close();
echo json_encode($response);
?>