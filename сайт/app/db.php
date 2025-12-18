<?php
/**
 * Простое подключение к базе данных MySQL для сайта «РукаПомощи».
 *
 * Перед использованием замените параметры $host, $dbname, $user, $pass
 * на реальные значения вашей базы данных.
 */

$host   = 'localhost';
$dbname = 'rukapomoshchi'; // имя БД
$user   = 'root';          // пользователь БД
$pass   = '';              // пароль БД
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$dbname;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (PDOException $e) {
    http_response_code(500);
    echo "Ошибка подключения к базе данных: " . htmlspecialchars($e->getMessage(), ENT_QUOTES, 'UTF-8');
    exit;
}

