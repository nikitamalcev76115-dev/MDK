<?php
/**
 * Конфигурация подключения к базе данных
 * RukaPomoshchi - Система управления волонтерскими проектами
 */

// Параметры подключения к MySQL
define('DB_HOST', 'localhost');
define('DB_NAME', 'rukapomoshchi');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_CHARSET', 'utf8mb4');

// Настройки для работы с БД
define('DB_OPTIONS', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,
]);

// Часовой пояс
date_default_timezone_set('Europe/Moscow');

// Кодировка
mb_internal_encoding('UTF-8');
mb_http_output('UTF-8');

