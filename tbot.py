#!/usr/bin/env python3
from __future__ import annotations
import logging, threading, time
from utils.command import bot
from utils.handlers import register_handlers
from utils.monitoring import monitor_system_resources_forever, version_monitoring_forever
from utils.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger('tbot')

def main():
    register_handlers()
    threading.Thread(target=monitor_system_resources_forever, daemon=True).start()
    threading.Thread(target=version_monitoring_forever, daemon=True).start()
    while True:
        try:
            logger.info('Starting polling')
            bot.infinity_polling(timeout=30, long_polling_timeout=30)
        except Exception:
            logger.exception('Polling crashed; retrying in 5s')
            time.sleep(5)

if __name__ == '__main__':
    main()
