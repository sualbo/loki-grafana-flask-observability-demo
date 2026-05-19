# Loki + Grafana + Flask Observability Demo

Учебный mini-project по развёртыванию стека наблюдаемости: **Flask-приложение отправляет структурированные логи в Loki, а Grafana автоматически показывает их на dashboard**.

Проект выполнен не как минимальная лабораторная работа, а как небольшой демонстрационный стенд для портфолио: всё поднимается через Docker Compose, Grafana получает Loki datasource автоматически, dashboard создаётся через provisioning, а приложение умеет генерировать тестовые логи разных уровней.

---

## Что показывает проект

Проект демонстрирует базовый сценарий observability для backend-приложения:

```text
Flask app → send_log_to_loki → Loki → Grafana datasource → Grafana dashboard
```

После запуска можно увидеть:

* последние логи приложения в Grafana;
* распределение логов по уровням `debug`, `info`, `warning`, `error`;
* работающую отправку логов через Loki Push API;
* автоматическое подключение Loki Data Source в Grafana;
* готовый dashboard без ручной настройки через интерфейс Grafana.

---

## Стек

* **Python 3.12**
* **Flask**
* **Docker / Docker Compose**
* **Grafana**
* **Grafana Loki**
* **LogQL**
* **Grafana provisioning**

---

## Структура проекта

```text
loki-grafana-logs-demo/
├── app/
│   ├── app.py
│   ├── loki_client.py
│   ├── log_generator.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
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
├── docs/
│   ├── ACCEPTANCE_CHECKLIST.md
│   └── CODEX_LOCAL_CHECK_PROMPT.md
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Быстрый запуск

Из корня проекта:

```bash
docker compose up -d --build
```

Проверить контейнеры:

```bash
docker compose ps
```

Ожидаемый результат: сервисы `loki`, `grafana` и `app` должны быть в состоянии `Up` / `running`.

---

## Доступные сервисы

| Сервис    | URL                                            | Назначение          |
| --------- | ---------------------------------------------- | ------------------- |
| Flask app | [http://localhost:5000](http://localhost:5000) | Тестовое приложение |
| Grafana   | [http://localhost:3000](http://localhost:3000) | Dashboard логов     |
| Loki      | [http://localhost:3100](http://localhost:3100) | Хранилище логов     |

Доступ в Grafana по умолчанию:

```text
login: admin
password: admin
```

При первом входе Grafana может предложить сменить пароль. Для локальной демонстрации можно пропустить этот шаг или задать временный пароль.

---

## Endpoint'ы Flask-приложения

| Endpoint                  | Описание                                         |
| ------------------------- | ------------------------------------------------ |
| `/`                       | Главная проверка приложения и отправка demo-лога |
| `/info`                   | Информация о приложении и Loki push URL          |
| `/calc/<a>/<b>`           | Пример endpoint'а с вычислением                  |
| `/log/info`               | Отправить один `info` лог                        |
| `/log/warning`            | Отправить один `warning` лог                     |
| `/log/error`              | Отправить один `error` лог                       |
| `/generate-logs?count=30` | Сгенерировать пачку тестовых логов               |

Пример генерации логов:

```bash
curl "http://localhost:5000/generate-logs?count=30"
```

---

## Проверка Loki

Проверить готовность Loki:

```bash
curl http://localhost:3100/ready
```

Проверить labels:

```bash
curl http://localhost:3100/loki/api/v1/labels
```

После генерации логов среди labels должны появиться:

```text
app
env
level
```

Пример значений:

```text
app="my_app"
level="debug" | "info" | "warning" | "error"
```

---

## Grafana Dashboard

После запуска проекта Grafana автоматически получает:

1. **Loki Data Source**
   URL внутри Docker Compose network:

   ```text
   http://loki:3100
   ```

2. **Dashboard: Loki App Logs Demo**

В dashboard есть две основные панели:

* таблица последних логов по запросу:

  ```logql
  {app="my_app"}
  ```

* круговая диаграмма распределения логов по уровню:

  ```logql
  sum by (level) (
    count_over_time({app="my_app"}[$__range])
  )
  ```

Для просмотра:

```text
Grafana → Dashboards → Loki Demo → Loki App Logs Demo
```

Рекомендуемый time range:

```text
Last 1 hour
```

После генерации логов нажать **Refresh**.

---

## Что было проверено локально

Проект был проверен локально через Docker Desktop + WSL.

Проверки:

* `python -m py_compile app/*.py`
* `docker compose config`
* `docker compose up -d --build`
* `docker compose ps`
* `curl http://localhost:3100/ready`
* `curl http://localhost:5000/`
* `curl http://localhost:5000/info`
* `curl "http://localhost:5000/generate-logs?count=30"`
* `curl http://localhost:3100/loki/api/v1/labels`
* проверка Loki labels: `app`, `env`, `level`
* проверка Loki query по `{app="my_app"}`
* проверка Grafana datasource через API
* проверка Grafana dashboard через API
* визуальная проверка dashboard в браузере

Фактический результат проверки:

* контейнеры `loki`, `grafana`, `app` запущены;
* Flask отвечает на запросы;
* Loki принимает логи и возвращает `204` на push;
* labels появляются в Loki;
* Grafana datasource создаётся автоматически;
* dashboard создаётся автоматически;
* таблица логов и круговая диаграмма отображаются в Grafana UI.

---

## Зачем это нужно в реальных проектах

Такой подход используется, когда приложение работает не только локально в терминале, а как сервис: в контейнере, на сервере, у клиента или в production-среде.

Логи помогают понять:

* что произошло в приложении;
* когда произошла ошибка;
* какой компонент её вызвал;
* увеличилось ли количество ошибок после обновления;
* какие операции проходят успешно, а какие ломаются.

Примеры реального применения:

* мониторинг backend API;
* наблюдение за Telegram-ботами;
* контроль интеграций с внешними API;
* диагностика ошибок в Docker-контейнерах;
* анализ поведения приложения после релиза.

---

## Особенности реализации

### Структурированные labels

Логи отправляются в Loki с labels:

```text
app="my_app"
env="demo"
level="info" / "warning" / "error" / "debug"
```

Это позволяет удобно фильтровать данные в LogQL.

### Безопасность

В проекте не используются секретные ключи и токены. Настройки вынесены в `.env.example` и переменные окружения.

Важно: это локальный учебный стенд. В production нельзя оставлять Grafana с доступом `admin/admin`, а также нельзя логировать пароли, токены, приватные сообщения, персональные и платёжные данные.

### Надёжность

Если Loki временно недоступен, Flask-приложение не падает. Функция `send_log_to_loki` возвращает структурированный результат доставки лога.

---

## Остановка проекта

Остановить контейнеры:

```bash
docker compose down
```

Остановить контейнеры и удалить volumes с данными Grafana/Loki:

```bash
docker compose down -v
```

Обычно для разработки достаточно:

```bash
docker compose down
```

---

## Возможные проблемы

### Docker Desktop не запущен

Если появляется ошибка подключения к Docker Engine или `dockerDesktopLinuxEngine`, нужно открыть Docker Desktop вручную и дождаться статуса `Docker Desktop is running`.

### В WSL не работает обычный docker

В некоторых конфигурациях WSL может потребоваться использовать Docker Desktop CLI из Windows или включить WSL Integration в настройках Docker Desktop.

### В Grafana нет логов

Проверить:

1. были ли сгенерированы логи;
2. работает ли Loki `/ready`;
3. есть ли labels в Loki;
4. выбран ли в Grafana time range `Last 1 hour`;
5. нажата ли кнопка `Refresh`.

### Loki падает из-за compactor / retention

В некоторых версиях Loki при включённом retention требуется корректная настройка compactor. В проекте конфигурация Loki уже адаптирована для локального demo-запуска.

---

## Статус проекта

Проект завершён как учебный mini-project и может использоваться как демонстрационный пример для GitHub/портфолио.

Он показывает навыки:

* Docker Compose;
* запуск нескольких сервисов в одной сети;
* Flask backend;
* отправка логов через HTTP API;
* Loki Push API;
* LogQL;
* Grafana provisioning;
* создание dashboard;
* базовая observability-инфраструктура для приложения.

---

## Возможные улучшения

Идеи для развития проекта:

* добавить Promtail или Alloy для сбора логов из файлов/контейнеров;
* добавить Grafana alerts для ошибок уровня `error`;
* добавить метрики приложения через Prometheus;
* добавить OpenTelemetry tracing;
* добавить отдельные dashboards для API latency и error rate;
* подготовить production-вариант с авторизацией, retention policy и безопасным хранением конфигурации.

---

## Краткое резюме

Этот проект показывает, как превратить обычное Flask-приложение в наблюдаемый сервис: приложение отправляет события в Loki, а Grafana визуализирует техническое состояние системы в dashboard.
