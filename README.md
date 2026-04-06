
# Hysteria Telegram Bot v2

Улучшенная версия Telegram-бота для управления Hysteria/Blitz CLI.

## Что улучшено

- безопасный запуск CLI без `shlex.split(command_string)`
- централизованная конфигурация через `.env`
- логирование
- таймауты subprocess
- единая проверка admin id
- разбиение длинных сообщений для Telegram
- systemd launcher
- модульная структура
- inline callback для действий с пользователем
- фоновый мониторинг CPU/RAM и проверки версии

## Структура

- `runbot.py` — старт/стоп systemd-сервиса
- `tbot.py` — точка входа
- `utils/` — логика бота
- `.env.example` — пример переменных

## Быстрый старт

1. Скопируй папку на сервер, например в `/opt/hysteria-bot-v2`
2. Создай venv:
   ```bash
   python3 -m venv /opt/hysteria-bot-v2/venv
   source /opt/hysteria-bot-v2/venv/bin/activate
   pip install -r /opt/hysteria-bot-v2/requirements.txt
   ```
3. Создай `.env`:
   ```bash
   cp /opt/hysteria-bot-v2/.env.example /opt/hysteria-bot-v2/.env
   nano /opt/hysteria-bot-v2/.env
   ```
4. Проверь, что CLI работает:
   ```bash
   python3 /etc/hysteria/core/cli.py list-users
   ```
5. Запусти:
   ```bash
   python3 /opt/hysteria-bot-v2/runbot.py start
   ```

## Переменные

- `API_TOKEN`
- `ADMIN_USER_IDS` — JSON-массив, например `[123456789]`
- `CLI_PATH`
- `BACKUP_DIRECTORY`
- `BACKUP_INTERVAL_HOUR`
- `CPU_ALERT_THRESHOLD`
- `RAM_ALERT_THRESHOLD`
- `COMMAND_TIMEOUT`

## Управление сервисом

```bash
python3 runbot.py start
python3 runbot.py stop
python3 runbot.py restart
python3 runbot.py status
python3 runbot.py set-backup-interval 12
```
