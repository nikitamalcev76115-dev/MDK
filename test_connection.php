<?php
/**
 * Тестовый файл для проверки подключения к базе данных
 * Откройте этот файл в браузере для проверки соединения
 */

require_once __DIR__ . '/db_connect.php';

?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Тест подключения к БД - RukaPomoshchi</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #f5c6cb;
        }
        .info {
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
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
    </style>
</head>
<body>
    <h1>Тест подключения к базе данных</h1>
    
    <?php
    try {
        $db = getDB();
        echo '<div class="success">✓ Подключение к базе данных успешно!</div>';
        
        // Проверка таблиц
        echo '<div class="info">';
        echo '<h2>Проверка таблиц:</h2>';
        
        $tables = ['roles', 'users', 'ngos', 'events', 'registrations', 'certificates'];
        foreach ($tables as $table) {
            try {
                $stmt = $db->query("SELECT COUNT(*) as count FROM $table");
                $result = $stmt->fetch();
                echo "<p>✓ Таблица '$table': {$result['count']} записей</p>";
            } catch (PDOException $e) {
                echo "<p>✗ Таблица '$table': не найдена</p>";
            }
        }
        echo '</div>';
        
        // Пример данных из таблицы events
        echo '<div class="info">';
        echo '<h2>Примеры мероприятий:</h2>';
        $stmt = $db->query("SELECT id, title, scheduled_at, location FROM events LIMIT 5");
        $events = $stmt->fetchAll();
        
        if (count($events) > 0) {
            echo '<table>';
            echo '<tr><th>ID</th><th>Название</th><th>Дата</th><th>Место</th></tr>';
            foreach ($events as $event) {
                echo '<tr>';
                echo '<td>' . htmlspecialchars($event['id']) . '</td>';
                echo '<td>' . htmlspecialchars($event['title']) . '</td>';
                echo '<td>' . htmlspecialchars($event['scheduled_at']) . '</td>';
                echo '<td>' . htmlspecialchars($event['location']) . '</td>';
                echo '</tr>';
            }
            echo '</table>';
        } else {
            echo '<p>Мероприятия не найдены. Запустите init_db.php для загрузки начальных данных.</p>';
        }
        echo '</div>';
        
        // Информация о подключении
        echo '<div class="info">';
        echo '<h2>Информация о подключении:</h2>';
        echo '<p><strong>Хост:</strong> ' . DB_HOST . '</p>';
        echo '<p><strong>База данных:</strong> ' . DB_NAME . '</p>';
        echo '<p><strong>Пользователь:</strong> ' . DB_USER . '</p>';
        echo '<p><strong>Кодировка:</strong> ' . DB_CHARSET . '</p>';
        echo '</div>';
        
    } catch (Exception $e) {
        echo '<div class="error">✗ Ошибка: ' . htmlspecialchars($e->getMessage()) . '</div>';
        echo '<div class="info">';
        echo '<h2>Проверьте:</h2>';
        echo '<ul>';
        echo '<li>Запущен ли MySQL сервер</li>';
        echo '<li>Правильны ли данные в config.php (DB_HOST, DB_NAME, DB_USER, DB_PASS)</li>';
        echo '<li>Существует ли база данных (запустите init_db.php для создания)</li>';
        echo '</ul>';
        echo '</div>';
    }
    ?>
    
    <div style="margin-top: 30px;">
        <a href="api.php?action=get_events" style="color: #007bff;">Тест API: Получить мероприятия</a> |
        <a href="api.php?action=get_roles" style="color: #007bff;">Тест API: Получить роли</a>
    </div>
</body>
</html>

