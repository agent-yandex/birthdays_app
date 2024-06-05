# Сервис для поздравления с днем рождения

## Установка

1. Развернуть Docker контрейнер с PosgreSQL

```bash
docker run -d --name fastapi_app -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -p 6233:5432 postgres:15.5
```

2. Установить зависимости

```bash
pip instal poetry
poetry install
```

3. Запустить миграции базы данных

```bash
alembic upgrade head
```

4. Запусить приложение

```bash
uvicorn app.main:app --reload --port 5100
```

## Использование

Все взаимодействие с приложением происзводится при помощи API, легче всего это делать через интерфейс FastAPI. Для просмотра автоматической документации нужно перейти на `http://127.0.0.1:5100/docs`

Авторизация пользователей производится при помощи JWT токена, авторизироваться можно в автоматической документации, нажав на кнопку `Authorize`

Данные для тестового пользователя:

* `username` - test_1
* `password` - password
