-- SQL скрипт для инициализации базы данных RukaPomoshchi
-- Запустите этот файл в MySQL для создания всех необходимых таблиц

CREATE DATABASE IF NOT EXISTS rukapomoshchi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE rukapomoshchi;

-- Таблица ролей
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица пользователей (волонтеров и НКО)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    total_hours INT DEFAULT 0,
    rating DECIMAL(5,2) DEFAULT 0.00,
    city VARCHAR(100) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица НКО (расширенная)
CREATE TABLE IF NOT EXISTS ngos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица мероприятий
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    ngo_id INT NOT NULL,
    scheduled_at DATETIME NOT NULL,
    location VARCHAR(200) DEFAULT NULL,
    max_volunteers INT DEFAULT NULL,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ngo_id) REFERENCES ngos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица регистраций на мероприятия
CREATE TABLE IF NOT EXISTS registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    volunteer_id INT NOT NULL,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    hours_earned INT DEFAULT 0,
    status ENUM('registered', 'completed', 'cancelled') DEFAULT 'registered',
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (volunteer_id) REFERENCES users(id),
    UNIQUE KEY unique_registration (event_id, volunteer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица сертификатов
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volunteer_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    hours_required INT DEFAULT 0,
    FOREIGN KEY (volunteer_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Вставка начальных данных: роли
INSERT IGNORE INTO roles (id, name) VALUES
(1, 'admin'),
(2, 'coordinator'),
(3, 'volunteer');

-- Вставка примера НКО
INSERT IGNORE INTO ngos (id, name, description) VALUES
(1, 'НКО «Город добрых дел»', 'Организация занимается проведением благотворительных мероприятий и марафонов.'),
(2, 'НКО «Поддержка рядом»', 'Онлайн поддержка и консультации для людей, оказавшихся в трудной ситуации.'),
(3, 'НКО «Чистый город»', 'Экологические инициативы, субботники и мероприятия по защите окружающей среды.');

-- Вставка примера мероприятий
INSERT IGNORE INTO events (id, title, description, ngo_id, scheduled_at, location, max_volunteers, status) VALUES
(1, 'Помощь в проведении благотворительного марафона', 'Регистрация участников, навигация по площадке, помощь организаторам. После участия часы будут учтены в системе и пойдут в ваш рейтинг.', 1, '2025-02-15 12:00:00', 'Москва, ВДНХ', 30, 'active'),
(2, 'Онлайн‑поддержка горячей линии НКО', 'Консультации по стандартным вопросам, помощь в навигации по программам поддержки. Рассматривается участие из любого региона.', 2, '2025-03-01 10:00:00', 'Онлайн', 20, 'active'),
(3, 'Экологический субботник в парке', 'Уборка территории, посадка деревьев, организация экологических квестов для детей.', 3, '2025-04-20 09:00:00', 'Москва, Сокольники', 50, 'active');

-- Вставка тестового пользователя-волонтера (пароль: password123, хеш bcrypt)
INSERT IGNORE INTO users (id, name, email, hashed_password, role_id, total_hours, rating, city) VALUES
(1, 'Иван Иванов', 'ivan@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 3, 126, 4.5, 'Москва'),
(2, 'Мария Петрова', 'maria@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 3, 89, 4.2, 'Санкт-Петербург');

-- Вставка примеров регистраций
INSERT IGNORE INTO registrations (event_id, volunteer_id, hours_earned, status) VALUES
(1, 1, 8, 'completed'),
(2, 1, 24, 'completed'),
(3, 1, 5, 'registered');

-- Вставка примеров сертификатов
INSERT IGNORE INTO certificates (volunteer_id, title, description, hours_required) VALUES
(1, 'Сертификат волонтера: Благотворительные мероприятия', 'За активное участие в благотворительных мероприятиях', 32),
(1, 'Сертификат волонтера: Экологические инициативы', 'За вклад в защиту окружающей среды', 5);

