<?php
/**
 * Пример использования PHP API для работы с базой данных
 * Этот файл демонстрирует различные способы взаимодействия с БД
 */

require_once __DIR__ . '/db_connect.php';

$db = getDB();

?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Примеры работы с БД - RukaPomoshchi</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #333;
        }
        .code {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #007bff;
            color: white;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
        }
        .btn:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <h1>Примеры работы с базой данных RukaPomoshchi</h1>
    
    <div class="section">
        <h2>1. Получить все мероприятия</h2>
        <div class="code">
            GET: api.php?action=get_events
        </div>
        <?php
        try {
            $stmt = $db->query("
                SELECT e.*, n.name as ngo_name
                FROM events e
                LEFT JOIN ngos n ON e.ngo_id = n.id
                WHERE e.status = 'active'
                ORDER BY e.scheduled_at ASC
            ");
            $events = $stmt->fetchAll();
            
            if (count($events) > 0) {
                echo '<table>';
                echo '<tr><th>ID</th><th>Название</th><th>НКО</th><th>Дата</th><th>Место</th></tr>';
                foreach ($events as $event) {
                    echo '<tr>';
                    echo '<td>' . htmlspecialchars($event['id']) . '</td>';
                    echo '<td>' . htmlspecialchars($event['title']) . '</td>';
                    echo '<td>' . htmlspecialchars($event['ngo_name']) . '</td>';
                    echo '<td>' . htmlspecialchars($event['scheduled_at']) . '</td>';
                    echo '<td>' . htmlspecialchars($event['location']) . '</td>';
                    echo '</tr>';
                }
                echo '</table>';
            } else {
                echo '<p>Мероприятия не найдены</p>';
            }
        } catch (Exception $e) {
            echo '<p style="color: red;">Ошибка: ' . htmlspecialchars($e->getMessage()) . '</p>';
        }
        ?>
    </div>
    
    <div class="section">
        <h2>2. Получить всех пользователей</h2>
        <div class="code">
            SELECT * FROM users
        </div>
        <?php
        try {
            $stmt = $db->query("
                SELECT u.id, u.name, u.email, u.city, u.total_hours, u.rating, r.name as role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                ORDER BY u.id ASC
            ");
            $users = $stmt->fetchAll();
            
            if (count($users) > 0) {
                echo '<table>';
                echo '<tr><th>ID</th><th>Имя</th><th>Email</th><th>Город</th><th>Роль</th><th>Часы</th><th>Рейтинг</th></tr>';
                foreach ($users as $user) {
                    echo '<tr>';
                    echo '<td>' . htmlspecialchars($user['id']) . '</td>';
                    echo '<td>' . htmlspecialchars($user['name']) . '</td>';
                    echo '<td>' . htmlspecialchars($user['email']) . '</td>';
                    echo '<td>' . htmlspecialchars($user['city']) . '</td>';
                    echo '<td>' . htmlspecialchars($user['role_name']) . '</td>';
                    echo '<td>' . htmlspecialchars($user['total_hours']) . '</td>';
                    echo '<td>' . htmlspecialchars($user['rating']) . '</td>';
                    echo '</tr>';
                }
                echo '</table>';
            } else {
                echo '<p>Пользователи не найдены</p>';
            }
        } catch (Exception $e) {
            echo '<p style="color: red;">Ошибка: ' . htmlspecialchars($e->getMessage()) . '</p>';
        }
        ?>
    </div>
    
    <div class="section">
        <h2>3. Получить все НКО</h2>
        <?php
        try {
            $stmt = $db->query("SELECT * FROM ngos ORDER BY name ASC");
            $ngos = $stmt->fetchAll();
            
            if (count($ngos) > 0) {
                echo '<table>';
                echo '<tr><th>ID</th><th>Название</th><th>Описание</th></tr>';
                foreach ($ngos as $ngo) {
                    echo '<tr>';
                    echo '<td>' . htmlspecialchars($ngo['id']) . '</td>';
                    echo '<td>' . htmlspecialchars($ngo['name']) . '</td>';
                    echo '<td>' . htmlspecialchars(substr($ngo['description'], 0, 100)) . '...</td>';
                    echo '</tr>';
                }
                echo '</table>';
            }
        } catch (Exception $e) {
            echo '<p style="color: red;">Ошибка: ' . htmlspecialchars($e->getMessage()) . '</p>';
        }
        ?>
    </div>
    
    <div class="section">
        <h2>4. Примеры использования API через JavaScript</h2>
        <div class="code">
// Получить все мероприятия
fetch('api.php?action=get_events')
    .then(response => response.json())
    .then(data => console.log(data));

// Регистрация пользователя
fetch('api.php?action=register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'Иван Иванов',
        email: 'ivan@example.com',
        password: 'password123',
        role_id: 3,
        city: 'Москва'
    })
})
.then(response => response.json())
.then(data => console.log(data));

// Вход в систему
fetch('api.php?action=login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        email: 'ivan@example.com',
        password: 'password123'
    })
})
.then(response => response.json())
.then(data => console.log(data));
        </div>
    </div>
    
    <div class="section">
        <h2>Полезные ссылки</h2>
        <a href="test_connection.php" class="btn">Тест подключения</a>
        <a href="api.php?action=get_events" class="btn">API: Мероприятия (JSON)</a>
        <a href="api.php?action=get_roles" class="btn">API: Роли (JSON)</a>
        <a href="api.php?action=get_ngos" class="btn">API: НКО (JSON)</a>
    </div>
</body>
</html>

