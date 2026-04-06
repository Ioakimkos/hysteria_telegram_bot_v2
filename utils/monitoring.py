from __future__ import annotations
import logging, time, re
import psutil
from .command import bot
from .config import settings
from .actions import check_version_text

logger = logging.getLogger(__name__)

def notify_admins(message: str):
    for admin_id in settings.admin_user_ids:
        try:
            bot.send_message(admin_id, message)
        except Exception:
            logger.exception('Failed to notify admin %s', admin_id)

def monitor_system_resources_forever():
    while True:
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            if cpu > settings.cpu_alert_threshold and ram > settings.ram_alert_threshold:
                time.sleep(60)
                cpu2 = psutil.cpu_percent(interval=1)
                ram2 = psutil.virtual_memory().percent
                if cpu2 > settings.cpu_alert_threshold and ram2 > settings.ram_alert_threshold:
                    notify_admins(f'🚨ALERT🚨\nHigh CPU and RAM usage detected\n\n📈 CPU: {cpu2:.1f}%\n📋 RAM: {ram2:.1f}%')
        except Exception:
            logger.exception('Resource monitoring failed')
        time.sleep(60)

def version_monitoring_forever():
    while True:
        try:
            result = check_version_text()
            panel = re.search(r'Panel Version: (\d+\.\d+\.\d+)', result)
            latest = re.search(r'Latest Version: (\d+\.\d+\.\d+)', result)
            if panel and latest and panel.group(1) != latest.group(1):
                notify_admins(f'🔔 New version available!\n\n{result}')
        except Exception:
            logger.exception('Version monitoring failed')
        time.sleep(86400)
