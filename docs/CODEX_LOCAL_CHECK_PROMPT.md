# Запрос для Codex в VS Code

Проверь этот проект локально в моей Windows/Docker Desktop среде.

Задачи:

1. Не меняй архитектуру без необходимости.
2. Запусти:

```bash
docker compose up -d --build
```

3. Проверь контейнеры:

```bash
docker ps
```

4. Проверь, что доступны:

```text
http://localhost:3000  # Grafana
http://localhost:3100/ready  # Loki
http://localhost:5000/health  # Flask app
```

5. Сгенерируй тестовые логи:

```bash
curl "http://localhost:5000/generate-logs?count=30"
```

6. Проверь labels в Loki:

```bash
curl http://localhost:3100/loki/api/v1/labels
```

7. Проверь, что Grafana provisioning подхватил:

- Loki datasource;
- dashboard `Loki App Logs Demo`.

8. Если есть ошибки в Docker Compose, Loki config, Grafana provisioning, dashboard JSON или Flask-приложении — исправь минимально необходимым изменением.

9. В конце дай краткий отчет:

- что запустилось;
- какие URL проверены;
- какие ошибки были найдены;
- какие файлы изменены;
- что осталось проверить вручную в Grafana UI.

Важно: не имитируй успешную проверку. Если что-то не работает, покажи реальную ошибку и исправь.
