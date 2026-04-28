<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

// Estrutura de resposta idêntica ao login.php
$response = array('success' => false, 'message' => '', 'data' => array());

// Usamos $_REQUEST para suportar GET e POST
$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos (username, password, database).';
    echo json_encode($response);
    exit;
}

$host = 'mysql'; // Nome do serviço no docker
$db_user = $username; 
$db_pass = $password;  

// 1. Criar conexão usando mysqli (seguindo a lógica do seu primeiro ficheiro)
$conn = new mysqli($host, $db_user, $db_pass, $database);

// 2. Verificar conexão
if ($conn->connect_error) {
    $response['message'] = "Erro de conexão MySQL: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// 3. Consulta
$sql = "SELECT id, tipoalerta, hora, msg, leitura, sensor FROM mensagens ORDER BY id DESC";
$result = $conn->query($sql);

if ($result) {
    $messages = array();
    while ($row = $result->fetch_assoc()) {
        $messages[] = $row;
    }
    
    $response['success'] = true;
    $response['data'] = $messages; // As mensagens vão aqui dentro
    $response['message'] = 'Mensagens carregadas com sucesso.';
} else {
    $response['message'] = 'Erro ao executar consulta: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>
