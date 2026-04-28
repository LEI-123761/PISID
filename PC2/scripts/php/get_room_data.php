<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

// Estrutura padrão para evitar erros de parse no Android
$response = array('success' => false, 'message' => '', 'data' => array());

// Usamos $_REQUEST para aceitar GET e POST
$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos (username, password, database).';
    echo json_encode($response);
    exit;
}

// Configuração para o ambiente Docker
$host = 'mysql'; 
$db_user = $username; 
$db_pass = $password; 

// 1. Criar conexão
$conn = new mysqli($host, $db_user, $db_pass, $database);

// 2. Verificar conexão
if ($conn->connect_error) {
    $response['message'] = "Erro de conexão MySQL: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// 3. Consulta
$sql = "SELECT Sala, NumeroMarsamisEven, NumeroMarsamisOdd FROM ocupacaolabirinto";
$result = $conn->query($sql);

if ($result) {
    $rooms = array();
    while ($row = $result->fetch_assoc()) {
        $rooms[] = $row;
    }
    
    $response['success'] = true;
    $response['data'] = $rooms;
    $response['message'] = 'Dados dos corredores carregados com sucesso.';
} else {
    $response['message'] = 'Erro ao executar consulta: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>