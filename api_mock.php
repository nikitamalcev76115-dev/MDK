<?php
/**
 * API для работы с in-memory базой данных (без реального MySQL)
 * Использует сессии PHP для хранения данных
 */

session_start();

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Обработка preflight запросов
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Инициализация хранилища в сессии
if (!isset($_SESSION['mock_db'])) {
    $_SESSION['mock_db'] = [
        'users' => [],
        'events' => [],
        'registrations' => [],
        'certificates' => [],
        'roles' => [
            ['id' => 1, 'name' => 'admin'],
            ['id' => 2, 'name' => 'coordinator'],
            ['id' => 3, 'name' => 'volunteer'],
        ],
        'ngos' => [
            ['id' => 1, 'name' => 'НКО «Город добрых дел»', 'description' => 'Организация занимается проведением благотворительных мероприятий.'],
            ['id' => 2, 'name' => 'НКО «Поддержка рядом»', 'description' => 'Онлайн поддержка и консультации.'],
            ['id' => 3, 'name' => 'НКО «Чистый город»', 'description' => 'Экологические инициативы и субботники.'],
        ],
        'next_user_id' => 1,
        'next_event_id' => 1,
        'next_registration_id' => 1,
        'next_certificate_id' => 1,
    ];
    
    // Добавляем примеры мероприятий
    $_SESSION['mock_db']['events'] = [
        [
            'id' => 1,
            'title' => 'Помощь в проведении благотворительного марафона',
            'description' => 'Регистрация участников, навигация по площадке, помощь организаторам.',
            'ngo_id' => 1,
            'scheduled_at' => date('Y-m-d H:i:s', strtotime('+30 days')),
            'location' => 'Москва, ВДНХ',
            'max_volunteers' => 30,
            'duration_hours' => 8,
            'status' => 'active'
        ],
        [
            'id' => 2,
            'title' => 'Онлайн‑поддержка горячей линии НКО',
            'description' => 'Консультации по стандартным вопросам, помощь в навигации.',
            'ngo_id' => 2,
            'scheduled_at' => date('Y-m-d H:i:s', strtotime('+15 days')),
            'location' => 'Онлайн',
            'max_volunteers' => 20,
            'duration_hours' => 4,
            'status' => 'active'
        ],
        [
            'id' => 3,
            'title' => 'Экологический субботник в парке',
            'description' => 'Уборка территории, посадка деревьев, организация экологических квестов.',
            'ngo_id' => 3,
            'scheduled_at' => date('Y-m-d H:i:s', strtotime('+45 days')),
            'location' => 'Москва, Сокольники',
            'max_volunteers' => 50,
            'duration_hours' => 5,
            'status' => 'active'
        ],
    ];
    $_SESSION['mock_db']['next_event_id'] = 4;
}

$db = &$_SESSION['mock_db'];
$method = $_SERVER['REQUEST_METHOD'];
$action = $_GET['action'] ?? '';

// Получение JSON данных из тела запроса
$input = json_decode(file_get_contents('php://input'), true);

try {
    switch ($action) {
        // Получить все мероприятия
        case 'get_events':
            if ($method === 'GET') {
                $events = array_map(function($event) use ($db) {
                    $ngo = array_filter($db['ngos'], function($n) use ($event) {
                        return $n['id'] == $event['ngo_id'];
                    });
                    $ngo = reset($ngo);
                    $event['ngo_name'] = $ngo ? $ngo['name'] : '';
                    return $event;
                }, $db['events']);
                echo json_encode(['success' => true, 'data' => array_values($events)], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Регистрация пользователя
        case 'register':
            if ($method === 'POST') {
                $name = $input['name'] ?? '';
                $email = $input['email'] ?? '';
                $password = $input['password'] ?? '';
                $role_id = intval($input['role_id'] ?? 3);
                $city = $input['city'] ?? '';
                
                if (empty($name) || empty($email) || empty($password)) {
                    throw new Exception('Не заполнены обязательные поля');
                }
                
                // Проверка существующего email
                foreach ($db['users'] as $user) {
                    if ($user['email'] === $email) {
                        throw new Exception('Пользователь с таким email уже существует');
                    }
                }
                
                // Хеширование пароля
                $hashed_password = password_hash($password, PASSWORD_BCRYPT);
                
                $new_user = [
                    'id' => $db['next_user_id']++,
                    'name' => $name,
                    'email' => $email,
                    'hashed_password' => $hashed_password,
                    'role_id' => $role_id,
                    'city' => $city,
                    'total_hours' => 0,
                    'rating' => 0.0,
                    'created_at' => date('Y-m-d H:i:s'),
                ];
                
                $db['users'][] = $new_user;
                
                echo json_encode([
                    'success' => true,
                    'message' => 'Пользователь зарегистрирован',
                    'id' => $new_user['id']
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
                
                $user = null;
                foreach ($db['users'] as $u) {
                    if ($u['email'] === $email) {
                        $user = $u;
                        break;
                    }
                }
                
                if (!$user || !password_verify($password, $user['hashed_password'])) {
                    throw new Exception('Неверный email или пароль');
                }
                
                // Находим роль
                $role = null;
                foreach ($db['roles'] as $r) {
                    if ($r['id'] == $user['role_id']) {
                        $role = $r;
                        break;
                    }
                }
                
                unset($user['hashed_password']);
                $user['role_name'] = $role ? $role['name'] : 'volunteer';
                
                echo json_encode([
                    'success' => true,
                    'message' => 'Вход выполнен успешно',
                    'user' => $user
                ], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Получить профиль пользователя
        case 'get_profile':
            if ($method === 'GET' && isset($_GET['user_id'])) {
                $user_id = intval($_GET['user_id']);
                
                $user = null;
                foreach ($db['users'] as $u) {
                    if ($u['id'] == $user_id) {
                        $user = $u;
                        break;
                    }
                }
                
                if (!$user) {
                    echo json_encode(['success' => false, 'message' => 'Пользователь не найден'], JSON_UNESCAPED_UNICODE);
                    break;
                }
                
                unset($user['hashed_password']);
                
                // Находим роль
                $role = null;
                foreach ($db['roles'] as $r) {
                    if ($r['id'] == $user['role_id']) {
                        $role = $r;
                        break;
                    }
                }
                $user['role_name'] = $role ? $role['name'] : 'volunteer';
                $user['role'] = $role;
                
                // Получить регистрации пользователя
                $user['registrations'] = array_filter($db['registrations'], function($r) use ($user_id) {
                    return $r['volunteer_id'] == $user_id;
                });
                $user['registrations'] = array_values($user['registrations']);
                
                // Получить сертификаты
                $user['certificates'] = array_filter($db['certificates'], function($c) use ($user_id) {
                    return $c['volunteer_id'] == $user_id;
                });
                $user['certificates'] = array_values($user['certificates']);
                
                echo json_encode(['success' => true, 'data' => $user], JSON_UNESCAPED_UNICODE);
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
                foreach ($db['registrations'] as $reg) {
                    if ($reg['event_id'] == $event_id && $reg['volunteer_id'] == $volunteer_id) {
                        throw new Exception('Вы уже зарегистрированы на это мероприятие');
                    }
                }
                
                $new_reg = [
                    'id' => $db['next_registration_id']++,
                    'event_id' => $event_id,
                    'volunteer_id' => $volunteer_id,
                    'registered_at' => date('Y-m-d H:i:s'),
                    'hours_earned' => 0,
                    'status' => 'registered'
                ];
                
                $db['registrations'][] = $new_reg;
                
                echo json_encode([
                    'success' => true,
                    'message' => 'Регистрация на мероприятие выполнена',
                    'id' => $new_reg['id']
                ], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Получить все НКО
        case 'get_ngos':
            if ($method === 'GET') {
                echo json_encode(['success' => true, 'data' => $db['ngos']], JSON_UNESCAPED_UNICODE);
            }
            break;
            
        // Получить все роли
        case 'get_roles':
            if ($method === 'GET') {
                echo json_encode(['success' => true, 'data' => $db['roles']], JSON_UNESCAPED_UNICODE);
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

