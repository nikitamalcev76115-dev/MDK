<?php
/**
 * API для работы с базой данных RukaPomoshchi
 * Обработка запросов для работы с пользователями, мероприятиями, регистрациями
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Обработка preflight запросов
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

require_once __DIR__ . '/db_connect.php';

$db = getDB();
$method = $_SERVER['REQUEST_METHOD'];
$action = $_GET['action'] ?? '';

// Получение JSON данных из тела запроса
$input = json_decode(file_get_contents('php://input'), true);

try {
    switch ($action) {
        // Получить все мероприятия
        case 'get_events':
            if ($method === 'GET') {
                $stmt = $db->query("
                    SELECT e.*, n.name as ngo_name, n.description as ngo_description
                    FROM events e
                    LEFT JOIN ngos n ON e.ngo_id = n.id
                    WHERE e.status = 'active'
                    ORDER BY e.scheduled_at ASC
                ");
                $events = $stmt->fetchAll();
                echo json_encode(['success' => true, 'data' => $events], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Получить мероприятие по ID
        case 'get_event':
            if ($method === 'GET' && isset($_GET['id'])) {
                $id = intval($_GET['id']);
                $stmt = $db->prepare("
                    SELECT e.*, n.name as ngo_name, n.description as ngo_description
                    FROM events e
                    LEFT JOIN ngos n ON e.ngo_id = n.id
                    WHERE e.id = ?
                ");
                $stmt->execute([$id]);
                $event = $stmt->fetch();
                if ($event) {
                    echo json_encode(['success' => true, 'data' => $event], JSON_UNESCAPED_UNICODE);
                } else {
                    echo json_encode(['success' => false, 'message' => 'Мероприятие не найдено'], JSON_UNESCAPED_UNICODE);
                }
            }
            break;
            
        // Создать мероприятие
        case 'create_event':
            if ($method === 'POST') {
                $title = $input['title'] ?? '';
                $description = $input['description'] ?? '';
                $ngo_id = intval($input['ngo_id'] ?? 0);
                $scheduled_at = $input['scheduled_at'] ?? '';
                $location = $input['location'] ?? '';
                $max_volunteers = intval($input['max_volunteers'] ?? 0);
                
                if (empty($title) || empty($ngo_id) || empty($scheduled_at)) {
                    throw new Exception('Не заполнены обязательные поля');
                }
                
                $stmt = $db->prepare("
                    INSERT INTO events (title, description, ngo_id, scheduled_at, location, max_volunteers, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'active')
                ");
                $stmt->execute([$title, $description, $ngo_id, $scheduled_at, $location, $max_volunteers]);
                
                echo json_encode([
                    'success' => true,
                    'message' => 'Мероприятие создано',
                    'id' => $db->lastInsertId()
                ], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Регистрация пользователя
        case 'register':
            if ($method === 'POST') {
                $name = $input['name'] ?? '';
                $email = $input['email'] ?? '';
                $password = $input['password'] ?? '';
                $role_id = intval($input['role_id'] ?? 3); // По умолчанию волонтер
                $city = $input['city'] ?? '';
                
                if (empty($name) || empty($email) || empty($password)) {
                    throw new Exception('Не заполнены обязательные поля');
                }
                
                // Проверка существующего email
                $stmt = $db->prepare("SELECT id FROM users WHERE email = ?");
                $stmt->execute([$email]);
                if ($stmt->fetch()) {
                    throw new Exception('Пользователь с таким email уже существует');
                }
                
                // Хеширование пароля
                $hashed_password = password_hash($password, PASSWORD_BCRYPT);
                
                $stmt = $db->prepare("
                    INSERT INTO users (name, email, hashed_password, role_id, city)
                    VALUES (?, ?, ?, ?, ?)
                ");
                $stmt->execute([$name, $email, $hashed_password, $role_id, $city]);
                
                echo json_encode([
                    'success' => true,
                    'message' => 'Пользователь зарегистрирован',
                    'id' => $db->lastInsertId()
                ], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Авторизация пользователя
        case 'login':
            if ($method === 'POST') {
                $email = $input['email'] ?? '';
                $password = $input['password'] ?? '';
                
                if (empty($email) || empty($password)) {
                    throw new Exception('Не заполнены email и пароль');
                }
                
                $stmt = $db->prepare("
                    SELECT u.*, r.name as role_name
                    FROM users u
                    LEFT JOIN roles r ON u.role_id = r.id
                    WHERE u.email = ?
                ");
                $stmt->execute([$email]);
                $user = $stmt->fetch();
                
                if ($user && password_verify($password, $user['hashed_password'])) {
                    // Удаляем пароль из ответа
                    unset($user['hashed_password']);
                    echo json_encode([
                        'success' => true,
                        'message' => 'Вход выполнен успешно',
                        'user' => $user
                    ], JSON_UNESCAPED_UNICODE);
                } else {
                    throw new Exception('Неверный email или пароль');
                }
            }
            break;
            
        // Регистрация на мероприятие
        case 'register_for_event':
            if ($method === 'POST') {
                $event_id = intval($input['event_id'] ?? 0);
                $volunteer_id = intval($input['volunteer_id'] ?? 0);
                
                if (empty($event_id) || empty($volunteer_id)) {
                    throw new Exception('Не указаны ID мероприятия или волонтера');
                }
                
                // Проверка существования регистрации
                $stmt = $db->prepare("SELECT id FROM registrations WHERE event_id = ? AND volunteer_id = ?");
                $stmt->execute([$event_id, $volunteer_id]);
                if ($stmt->fetch()) {
                    throw new Exception('Вы уже зарегистрированы на это мероприятие');
                }
                
                $stmt = $db->prepare("
                    INSERT INTO registrations (event_id, volunteer_id, status)
                    VALUES (?, ?, 'registered')
                ");
                $stmt->execute([$event_id, $volunteer_id]);
                
                echo json_encode([
                    'success' => true,
                    'message' => 'Регистрация на мероприятие выполнена',
                    'id' => $db->lastInsertId()
                ], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Получить профиль пользователя
        case 'get_profile':
            if ($method === 'GET' && isset($_GET['user_id'])) {
                $user_id = intval($_GET['user_id']);
                
                $stmt = $db->prepare("
                    SELECT u.*, r.name as role_name
                    FROM users u
                    LEFT JOIN roles r ON u.role_id = r.id
                    WHERE u.id = ?
                ");
                $stmt->execute([$user_id]);
                $user = $stmt->fetch();
                
                if ($user) {
                    unset($user['hashed_password']);
                    
                    // Получить регистрации пользователя
                    $stmt = $db->prepare("
                        SELECT r.*, e.title as event_title, e.scheduled_at, e.location
                        FROM registrations r
                        LEFT JOIN events e ON r.event_id = e.id
                        WHERE r.volunteer_id = ?
                        ORDER BY r.registered_at DESC
                    ");
                    $stmt->execute([$user_id]);
                    $user['registrations'] = $stmt->fetchAll();
                    
                    // Получить сертификаты
                    $stmt = $db->prepare("
                        SELECT * FROM certificates
                        WHERE volunteer_id = ?
                        ORDER BY issued_at DESC
                    ");
                    $stmt->execute([$user_id]);
                    $user['certificates'] = $stmt->fetchAll();
                    
                    echo json_encode(['success' => true, 'data' => $user], JSON_UNESCAPED_UNICODE);
                } else {
                    echo json_encode(['success' => false, 'message' => 'Пользователь не найден'], JSON_UNESCAPED_UNICODE);
                }
            }
            break;
            
        // Получить все НКО
        case 'get_ngos':
            if ($method === 'GET') {
                $stmt = $db->query("SELECT * FROM ngos ORDER BY name ASC");
                $ngos = $stmt->fetchAll();
                echo json_encode(['success' => true, 'data' => $ngos], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Получить все роли
        case 'get_roles':
            if ($method === 'GET') {
                $stmt = $db->query("SELECT * FROM roles ORDER BY id ASC");
                $roles = $stmt->fetchAll();
                echo json_encode(['success' => true, 'data' => $roles], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        default:
            echo json_encode([
                'success' => false,
                'message' => 'Неизвестное действие. Используйте параметр ?action=...'
            ], JSON_UNESCAPED_UNICODE);
    }
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ], JSON_UNESCAPED_UNICODE);
}

