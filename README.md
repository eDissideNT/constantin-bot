# Constantin Bot

Telegram бот-конструктор для создания и управления ботами-нотификаторами. Позволяет создавать дочерних ботов, каждый из которых работает по собственному сценарию из таблицы NocoDB.

## Компоненты

| Сервис | Описание |
|---|---|
| **postgres** | PostgreSQL 16 — реестр ботов (`constructor`) и данные NocoDB (`nocodb`) |
| **nocodb** | Веб-интерфейс для сценариев ботов — `http://localhost:8080` |
| **constructor** | TypeScript-бот + Python 3.12 + PM2 для дочерних ботов |

## Первый запуск (инициализация)

1. Скопировать и заполнить переменные окружения:
   ```
   cp .env.example .env
   ```
   Обязательные значения: `POSTGRES_PASSWORD`, `CONSTRUCTOR_DB_PASSWORD`, `NC_AUTH_JWT_SECRET`, `CONSTRUCTOR_BOT_TOKEN`

2. Запустить инфраструктуру:
   ```
   docker compose up -d
   ```

3. Открыть `http://localhost:8080`, создать аккаунт администратора NocoDB, затем в **Team & Settings → API Tokens** сгенерировать токен.

4. Добавить токен в `.env`:
   ```
   NOCODB_API_TOKEN=<сгенерированный токен>
   ```

5. Перезапустить конструктор:
   ```
   docker compose restart constructor
   ```

## Запуск

```bash
docker compose up -d                     # запустить все сервисы
docker compose down                      # остановить все сервисы
docker compose logs -f constructor       # логи конструктора
```
