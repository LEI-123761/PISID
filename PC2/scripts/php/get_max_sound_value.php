<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

// Estrutura padrão para o seu Android processar sem erros
$response = array('success' => false, 'message' => '', 'data' => null);

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

// Conexão mysqli
$conn = new mysqli($host, $db_user, $db_pass, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de conexão: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// Query para obter o valor máximo de som
$sql = "SELECT maximo FROM configsound LIMIT 1";
$result = $conn->query($sql);

if ($result) {
    $row = $result->fetch_assoc();
    
    if ($row) {
        $response['success'] = true;
        $response['data'] = $row; // Retorna o objeto: {"maximo": "valor"}
        $response['message'] = 'Configuração de som carregada.';
    } else {
        $response['message'] = 'Nenhuma configuração de som encontrada.';
    }
} else {
    $response['message'] = "Erro na query: " . $conn->error;
}

$conn->close();
echo json_encode($response);
?>