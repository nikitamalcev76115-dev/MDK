<?php
/**
 * Скрипт для инициализации базы данных
 * Создает базу данных и таблицы, если их еще нет
 * Запустите этот файл один раз для настройки БД
 */

require_once __DIR__ . '/config.php';

try {
    // Подключение без указания базы данных для создания БД
    $dsn = "mysql:host=" . DB_HOST . ";charset=" . DB_CHARSET;
    $pdo = new PDO($dsn, DB_USER, DB_PASS, DB_OPTIONS);
    
    // Создание базы данных, если её нет
    $pdo->exec("CREATE DATABASE IF NOT EXISTS " . DB_NAME . " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
    $pdo->exec("USE " . DB_NAME);
    
    echo "База данных '" . DB_NAME . "' создана или уже существует.\n";
    
    // Чтение SQL файла
    $sqlFile = __DIR__ . '/app/init_db.sql';
    if (!file_exists($sqlFile)) {
        throw new Exception("Файл init_db.sql не найден!");
    }
    
    $sql = file_get_contents($sqlFile);
    
    // Удаляем команды CREATE DATABASE и USE из SQL, так как БД уже создана
    $sql = preg_replace('/CREATE DATABASE.*?;/i', '', $sql);
    $sql = preg_replace('/USE.*?;/i', '', $sql);
    
    // Разделяем SQL на отдельные запросы
    $queries = array_filter(
        array_map('trim', explode(';', $sql)),
        function($query) {
            return !empty($query) && !preg_match('/^--/', $query);
        }
    );
    
    // Выполняем каждый запрос
    foreach ($queries as $query) {
        if (!empty(trim($query))) {
            try {
                $pdo->exec($query);
            } catch (PDOException $e) {
                // Игнорируем ошибки типа "таблица уже существует"
                if (strpos($e->getMessage(), 'already exists') === false && 
                    strpos($e->getMessage(), 'Duplicate') === false) {
                    echo "Предупреждение: " . $e->getMessage() . "\n";
                }
            }
        }
    }
    
    echo "Таблицы созданы успешно!\n";
    echo "Начальные данные загружены.\n";
    echo "\nБаза данных готова к использованию!\n";
    
} catch (PDOException $e) {
    die("Ошибка при инициализации базы данных: " . $e->getMessage() . "\n");
} catch (Exception $e) {
    die("Ошибка: " . $e->getMessage() . "\n");
}

