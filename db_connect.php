<?php
/**
 * Подключение к базе данных MySQL
 * Использует PDO для безопасной работы с БД
 */

require_once __DIR__ . '/config.php';

class Database {
    private static $instance = null;
    private $connection;
    
    /**
     * Приватный конструктор для паттерна Singleton
     */
    private function __construct() {
        try {
            $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
            $this->connection = new PDO($dsn, DB_USER, DB_PASS, DB_OPTIONS);
        } catch (PDOException $e) {
            // В продакшене лучше логировать ошибку, а не выводить
            die("Ошибка подключения к базе данных: " . $e->getMessage());
        }
    }
    
    /**
     * Получить единственный экземпляр подключения (Singleton)
     */
    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    /**
     * Получить объект PDO подключения
     */
    public function getConnection() {
        return $this->connection;
    }
    
    /**
     * Предотвратить клонирование
     */
    private function __clone() {}
    
    /**
     * Предотвратить десериализацию
     */
    public function __wakeup() {
        throw new Exception("Cannot unserialize singleton");
    }
}

/**
 * Функция-хелпер для получения подключения к БД
 */
function getDB() {
    return Database::getInstance()->getConnection();
}

// Тест подключения (можно удалить в продакшене)
try {
    $db = getDB();
    // echo "Подключение к базе данных успешно!";
} catch (Exception $e) {
    die("Ошибка: " . $e->getMessage());
}

