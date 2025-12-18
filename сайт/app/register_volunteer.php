<?php
/**
 * Пример: сохранение регистрации волонтера в MySQL.
 * Ожидает POST‑запрос с полями:
 *  first_name, last_name, email, city
 */

require __DIR__ . '/db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo "Метод не поддерживается";
    exit;
}

// Простая валидация
$firstName = trim($_POST['first_name'] ?? '');
$lastName  = trim($_POST['last_name'] ?? '');
$email     = trim($_POST['email'] ?? '');
$city      = trim($_POST['city'] ?? '');

if ($firstName === '' || $lastName === '' || $email === '') {
    http_response_code(400);
    echo "Заполните имя, фамилию и email.";
    exit;
}

try {
    // Таблица volunteers (id, first_name, last_name, email, city, created_at)
    $stmt = $pdo->prepare(
        "INSERT INTO volunteers (first_name, last_name, email, city, created_at)
         VALUES (:first_name, :last_name, :email, :city, NOW())"
    );
    $stmt->execute([
        ':first_name' => $firstName,
        ':last_name'  => $lastName,
        ':email'      => $email,
        ':city'       => $city,
    ]);

    echo "Регистрация успешно сохранена!";
} catch (PDOException $e) {
    http_response_code(500);
    echo "Ошибка при сохранении: " . htmlspecialchars($e->getMessage(), ENT_QUOTES, 'UTF-8');
}


