# Acceptance checklist

Используй этот чек-лист перед сдачей задания.

## 1. Docker Compose

```bash
docker compose up -d --build
docker ps
```

Ожидается:

- `loki-demo` в состоянии running;
- `grafana-demo` в состоянии running;
- `flask-loki-demo-app` в состоянии running.

## 2. Loki

```bash
curl http://localhost:3100/ready
```

Ожидается ответ `ready` или HTTP 200.

## 3. Flask app

```bash
curl http://localhost:5000/health
curl http://localhost:5000/info
curl http://localhost:5000/calc/2/3
```

Ожидается JSON-ответ без 500-ошибок.

## 4. Генерация логов

```bash
curl "http://localhost:5000/generate-logs?count=30"
```

Ожидается, что `successfully_sent` больше 0.

## 5. Loki labels

```bash
curl http://localhost:3100/loki/api/v1/labels
```

Ожидается наличие labels:

- `app`
- `env`
- `level`

## 6. Grafana

Открыть:

```text
http://localhost:3000
```

Логин:

```text
admin / admin
```

Проверить:

- Data Source `Loki` существует;
- dashboard `Loki App Logs Demo` существует;
- панель последних логов показывает записи;
- pie chart показывает распределение по level.

## 7. Остановка

```bash
docker compose down
```
