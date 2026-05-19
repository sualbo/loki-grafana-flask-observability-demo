# Loki + Grafana + Flask Observability Demo

Учебный проект для развёртывания локального стека наблюдаемости:

- **Loki** принимает логи через HTTP Push API.
- **Grafana** автоматически подключает Loki как Data Source.
- **Flask-приложение** отправляет логи в Loki через функцию `send_log_to_loki`.
- **Dashboard** создаётся автоматически и показывает последние логи + распределение логов по уровню.

## Портфолио-фича

**Observability Demo Pack**: проект запускается одной командой и сразу содержит готовый Grafana Data Source, dashboard и генератор тестовых логов.

Это делает проект демонстрационным: можно показать полный путь данных:

```text
Flask endpoint -> send_log_to_loki -> Loki Push API -> Loki labels -> Grafana dashboard
```

## Структура проекта

```text
loki-grafana-logs-demo/
├── app/
│   ├── app.py                 # Flask endpoints
│   ├── loki_client.py          # send_log_to_loki и сборка Loki payload
│   ├── log_generator.py        # генератор демонстрационных логов
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── docs/
│   ├── ACCEPTANCE_CHECKLIST.md
│   └── CODEX_LOCAL_CHECK_PROMPT.md
├── grafana/
│   ├── dashboards/
│   │   └── loki-app-logs-dashboard.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboard-provider.yml
│       └── datasources/
│           └── loki.yml
├── loki/
│   └── loki-config.yml
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Быстрый запуск

Требования:

- Docker Desktop запущен.
- Порты `3000`, `3100`, `5000` свободны.

Из корня проекта:

```bash
docker compose up -d --build
```

Проверить контейнеры:

```bash
docker ps
```

Ожидаемые сервисы:

- `grafana-demo` — Grafana на <http://localhost:3000>
- `loki-demo` — Loki на <http://localhost:3100>
- `flask-loki-demo-app` — Flask на <http://localhost:5000>

## Доступ в Grafana

Открой:

```text
http://localhost:3000
```

Логин по умолчанию:

```text
admin / admin
```

После входа открой dashboard:

```text
Dashboards -> Loki Demo -> Loki App Logs Demo
```

Data Source Loki создаётся автоматически через provisioning.

## Генерация тестовых логов

Открой в браузере или вызови через curl:

```bash
curl http://localhost:5000/
curl http://localhost:5000/info
curl http://localhost:5000/calc/2/3
curl http://localhost:5000/log/info
curl http://localhost:5000/log/warning
curl http://localhost:5000/log/error
curl "http://localhost:5000/generate-logs?count=30"
```

После этого обнови dashboard в Grafana.

## Основные LogQL-запросы

Последние логи приложения:

```logql
{app="my_app"}
```

Распределение логов по уровню за выбранный диапазон времени:

```logql
sum by (level) (count_over_time({app="my_app"}[$__range]))
```

## Проверка Loki напрямую

Проверить готовность Loki:

```bash
curl http://localhost:3100/ready
```

Посмотреть labels:

```bash
curl http://localhost:3100/loki/api/v1/labels
```

Если логи уже отправлены, среди labels должны появиться:

```text
app
env
level
```

## Что реализовано по заданию

### Часть 1. Развёртывание стека и подключение источника

- `docker-compose.yml` поднимает `loki` и `grafana`.
- Loki доступен внутри compose-сети как `http://loki:3100`.
- Grafana доступна с хоста как `http://localhost:3000`.
- Data Source Loki создаётся автоматически через `grafana/provisioning/datasources/loki.yml`.

### Часть 2. Визуализация логов в Grafana

Dashboard содержит две панели:

1. **Последние логи приложения `{app="my_app"}`**.
2. **Pie chart распределения логов по `level`**.

### Часть 3. Интеграция отправки логов

В `app/loki_client.py` реализована функция:

```python
send_log_to_loki(level: str, message: str, **fields)
```

Она отправляет POST-запрос на:

```text
/loki/api/v1/push
```

## Важные технические решения

### Почему внутри Docker используется `http://loki:3100`

Контейнер Flask-приложения находится в одной Docker Compose-сети с Loki. Поэтому из контейнера приложения надо обращаться к Loki по имени сервиса:

```text
http://loki:3100/loki/api/v1/push
```

`localhost` внутри контейнера приложения указывал бы на сам контейнер приложения, а не на Loki.

### Почему timestamp передаётся строкой

В Loki Push API timestamp должен быть строкой. В проекте используется:

```python
str(time.time_ns())
```

Это Unix timestamp в наносекундах.

### Почему labels не перегружены

В labels вынесены только стабильные поля:

- `app`
- `env`
- `level`

Детали запроса и дополнительные поля записываются внутрь JSON log line. Это снижает риск высокой кардинальности labels.

## Типовые проблемы и решения

### Grafana открывается, но dashboard пустой

Сначала сгенерируй логи:

```bash
curl "http://localhost:5000/generate-logs?count=30"
```

Потом обнови dashboard и проверь диапазон времени: `Last 1 hour`.

### Loki datasource сообщает, что labels отсутствуют

Проверь:

1. Приложение реально отправляло логи.
2. Внутренний URL в контейнере приложения: `http://loki:3100/loki/api/v1/push`.
3. Контейнеры находятся в одной compose-сети.
4. `curl http://localhost:3100/loki/api/v1/labels` возвращает labels после генерации логов.

### Порт 3000, 3100 или 5000 занят

Останови конфликтующий сервис или измени порт в `docker-compose.yml`.

Например, для Grafana:

```yaml
ports:
  - "3001:3000"
```

Тогда Grafana будет доступна на `http://localhost:3001`.

### Полностью пересоздать стек

```bash
docker compose down -v
docker compose up -d --build
```

Команда `down -v` удалит volume с данными Loki и Grafana.

## Как остановить проект

Остановить контейнеры, сохранив volumes:

```bash
docker compose down
```

Остановить и удалить данные:

```bash
docker compose down -v
```

## Локальная проверка через Codex

После распаковки проекта можно открыть папку в VS Code и дать Codex запрос из файла:

```text
docs/CODEX_LOCAL_CHECK_PROMPT.md
```

Codex должен запускать и проверять проект именно в твоей локальной Windows/Docker Desktop среде.

## Ограничения

- Проект предназначен для локального учебного запуска, не для production.
- Авторизация Loki отключена: `auth_enabled: false`.
- Grafana использует demo-логин `admin/admin`.
- Retention Loki настроен как короткий demo-режим.
- Для production понадобятся авторизация, TLS, секреты вне репозитория, backup, resource limits, monitoring самого стека.

## Project status: locally tested

Verified:
- docker compose up -d --build
- Loki /ready
- Flask endpoints
- log generation
- Loki labels
- Grafana datasource provisioning
- Grafana dashboard provisioning
- visual check in Grafana UI