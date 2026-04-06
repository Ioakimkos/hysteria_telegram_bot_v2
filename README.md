# Hysteria Telegram Bot v2.2

Что добавлено:
- Inline UI вместо текстовых действий для карточки пользователя
- Telegram Dashboard с онлайном, трафиком, server info и кнопкой refresh
- Безопасный запуск CLI через список аргументов
- Systemd launcher
- Monitoring CPU/RAM + version check

## Установка
```bash
cd /opt
unzip hysteria_telegram_bot_v2_2.zip -d hysteria-bot-v2_2
cd hysteria-bot-v2_2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python3 runbot.py start
```
