## Проект «РукаПомощи» — система управления волонтёрскими проектами

Backend на **FastAPI** по теме МДК:

- **НКО публикуют мероприятия**
- **Волонтёры записываются на события**
- **Учет часов, рейтинг, сертификаты**
- **Разграничение прав (admin / volunteer)**

### Установка

1. Установите зависимости (виртуальное окружение по желанию):

```bash
pip install -r requirements.txt
```

2. (Опционально) создайте файл `.env` рядом с `main.py`:

```env
SECRET_KEY=ej08rj4wg09dnviesr03wjg
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DB_NAME=test.db
```

### Запуск

Команда из задания:

```bash
uvicorn main:app --reload
```

После запуска:

- документация Swagger: `http://127.0.0.1:8000/docs`
- главная проверка: `http://127.0.0.1:8000/`

### Основные сущности и функционал

- **Роли**: `admin`, `volunteer`
- **Пользователи**:
  - `POST /auth/register` — регистрация волонтёра (name, email, password)
  - `POST /auth/login` — логин (OAuth2, возвращает JWT-токен)
- **Роли**:
  - `GET /roles/` — получить список ролей (только admin по JWT)
- **Мероприятия**:
  - `GET /events/` — список мероприятий
  - `POST /events/` — создать мероприятие (только admin)
  - `POST /events/{event_id}/signup` — записаться на мероприятие (волонтёр по JWT)
  - `POST /events/{event_id}/complete` — завершить мероприятие, начислить часы волонтёрам (admin)
  - `POST /events/certificates/{volunteer_id}` — выдать сертификат волонтёру (admin)

Данные сейчас хранятся в памяти (по аналогии с `shop_db` из примера), чего достаточно для учебного репозитория.

### Примеры запросов с fetch (frontend)

Регистрация (фрагмент из задания адаптирован под наш backend):

```javascript
try {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: name,
      email: email,
      password: password,
    }),
  });
  const data = await response.json();
  console.log(data);
} catch (e) {
  console.error(e);
}
```

Получение списка мероприятий:

```javascript
const response = await fetch('/events/');
if (!response.ok) {
  throw new Error(`HTTP error! status: ${response.status}`);
}
const events = await response.json();
console.log(events);
```

# RukaPomoshchi — система волонтёрских проектов (FastAPI)

Минимальный учебный проект по МДК: система управления волонтёрскими проектами «РукаПомощи».

- НКО публикуют мероприятия, волонтёры записываются на события  
- Учёт часов, рейтинговая система, управление компетенциями (пока в виде заглушек)  
- Примеры разграничения ролей (admin), регистрации и работы с API через `fetch`

## Установка

```bash
cd "C:\\Users\\nikit\\OneDrive\\Рабочий стол\\сайт"
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

## Запуск backend

```bash
uvicorn main:app --reload
```

После запуска:

- Swagger-документация: `http://127.0.0.1:8000/docs`
- Главная API: `http://127.0.0.1:8000/`
- Статичная страница (frontend): `http://127.0.0.1:8000/static/index.html`

## Основные эндпоинты

- `GET /` — описание проекта «РукаПомощи»  
- `GET /shop/products/` — пример магазина (фрагменты MyShop из задания)  
- `GET /api/roles` — пример разграничения прав через `check_is_admin` / `IsAdminDep`  
- `POST /auth/register` — регистрация волонтёра (пример `fetch(AUTH_ENDPOINTS.REGISTER, ...)`)  
- `GET /api/trips?waybill_id=...` — пример `fetch(\`${TRIPS_API}?waybill_id=\${waybillId}\`)`

Фронтенд-страница (`static/index.html`) визуально показывает эти возможности и отправляет запросы через `fetch`.



