# API-сервис сокращения ссылок

[Ноутбук](./client.ipynb) с демонстрацией функционала

## Запуск сервиса

```
docker compose up --build
```

## Особенности проекта

- JWT-авторизация
- PostgreSQL для хранения данных приложения
- Redis для кэширования запросов

## Структура проекта

```
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── src
    ├── auth
    │   ├── router.py
    │   ├── schemas.py
    │   └── utils.py
    ├── links
    │   ├── router.py
    │   └── schemas.py
    ├── main.py
    ├── config.py
    └── database.py
```

### Основные модули/компоненты

- `Dockerfile` - описание Docker-образа для контейнеризации основного fastapi-приложения
- `docker-compose.yml` - инструкции для развертывания мультиконтейнерного приложения (postgres, redis, основное fastapi приложение)
- `requirements.txt` - зависимости приложения
- `src/` - директория для хранения логики основного приложения
- `src/auth/` / `src/links/` - директории, в которых хранится логика авторизации и основного функцоанала API соответственно
- `src/*router.py` - подключаемые роутеры
- `src/*schemas.py` - описание SQLModel и Pydantic моделей
- `src/main.py` - entrypoint основного приложения
- `src/config.py` - загрузка переменных окружения
- `src/database.py` - определение движка SQLAlchemy и функции получения сессиии для работы с БД
 
## Endpoints

- `POST "/register"` - регистрация нового пользователя

Пример запроса: `curl -X 'POST' 'BASEURL/register' -d '{"email": "user@example.com", "password": "string"}'`

Пример успешного ответа: 
```
{
  "id": 1,
  "email": "user@example.com",
  "registered_at": "2025-03-24T14:54:55.154272"
}
```

- `POST "/login"` - авторизация существующего пользователя, возвращает Access Token

Пример запроса: `curl -X 'POST' 'BASEURL/login' -d '{"email": "user@example.com", "password": "string"}'`

Пример успешного ответа: 
```
{
  "access_token": "string",
  "token_type": "string"
}
```

- `GET "/users/me"` - получение информации о текущем пользователе

Пример запроса: `curl -X 'GET' 'BASEURL/users/me'`

Пример успешного ответа: 
```
{
  "id": 1,
  "email": "user@example.com",
  "registered_at": "2025-03-24T14:54:55.154272"
}
```

- `POST "/links/shorten"` - создание короткой ссылки

Пример запроса: `curl -X 'GET' 'BASEURL/links/shorten' -d '{"original_url": "https://example.com/", "custom_alias": "string", "expires_at": "2025-04-24T15:16:29.769Z"}'`

Параметры `custom_alias` и `expires_at` - опциональные, в случае отсутствия `expires_at` будет задан значением по умолчанию относительно текущей даты, `custom_alias` будет сгенерирован автоматически

Пример успешного ответа: 
```
{
  "original_url": "https://example.com/",
  "short_code": "string",
  "created_at": "2025-03-24T15:16:41.868Z",
  "expires_at": "2025-04-24T15:16:41.868Z"
}
```

- `GET "/links/search"` (cached) - поиск коротких ссылок по оригинальному URL 

Пример запроса: `curl -X 'GET' 'BASEURL/links/search?original_url=https://example.com/'`

Пример успешного ответа: 
```
[{
  "original_url": "https://example.com/",
  "short_code": "string",
  "created_at": "2025-03-24T15:16:41.868Z",
  "expires_at": "2025-04-24T15:16:41.868Z"
},
{
  "original_url": "https://example.com/",
  "short_code": "string1",
  "created_at": "2025-03-24T15:16:41.868Z",
  "expires_at": "2025-04-24T15:16:41.868Z"
}]
```

- `GET "/links/{short_code}/stats"` (cached) - получение статистики обращений по короткой ссылке

Пример запроса: `curl -X 'GET' 'BASEURL/links/string/stats'`

Пример успешного ответа: 
```
{
  "short_code": "string",
  "created_at": "2025-03-24T15:27:00.133Z",
  "last_requested": "2025-03-24T15:27:00.133Z",
  "num_requests": 1
}
```

- `GET "/links/{short_code}"` - переход на оригинальный URL по короткой ссылке (redirect)

Пример запроса: `curl -X 'GET' 'BASEURL/links/string'`

- `DELETE "/links/{short_code}"` - удаление связи короткой и оригинальной ссылки

Пример запроса: `curl -X 'DELETE' 'BASEURL/links/string'`

- `PUT "/links/{short_code}"` - привязка нового URL к короткой ссылке

Пример запроса: `curl -X 'PUT' 'BASEURL/links/string?new_url=https://example.com/'`

Пример успешного ответа: 
```
{
  "original_url": "https://example.com/",
  "short_code": "string",
  "created_at": "2025-03-24T15:16:41.868Z",
  "expires_at": "2025-04-24T15:16:41.868Z"
}
```

## Описание объектов БД

- Таблица `users` - таблица с данными пользователей, содержит email, дату регистрации и хэшированный пароль

Definition: `/src/auth/schemas`

- Таблица `short_urls` - таблица привязок коротких ссылок к оригинальным, содержит информацию о времени создания и экспирации, а также пользователе, создавшим привязку

Definition: `/src/links/schemas`

- Таблица `requests_log` - лог обращений (переходов) по короткой ссылке, используется для сбора статистики

Definition: `/src/links/schemas`


## Разное

- Кэшируются наиболее "тяжелые" для БД запросы - поиск по оригинальному URL и получение статистики
- Редактирование и удаление коротких ссылок доступно только их создателю
- Есть механизм удаления из БД истекших ссылок - оно происходит при первом вызове после заданного для ссылки времени экспирации
