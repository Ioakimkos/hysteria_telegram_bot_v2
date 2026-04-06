from __future__ import annotations
import subprocess, logging
from typing import Sequence
import telebot
from .config import settings

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(settings.api_token, parse_mode='Markdown')

def is_admin(user_id: int) -> bool:
    return int(user_id) in settings.admin_user_ids

def run_cli_command(args: Sequence[str]) -> str:
    try:
        p = subprocess.run(list(args), capture_output=True, text=True, timeout=settings.command_timeout, check=False)
    except subprocess.TimeoutExpired:
        return 'Error: command timed out'
    except Exception as e:
        logger.exception('Command failed')
        return f'Error: {e}'
    out = (p.stdout or '').strip()
    err = (p.stderr or '').strip()
    if p.returncode != 0:
        return f"Error:\n{err or out or ('exit code ' + str(p.returncode))}"
    return out or 'OK'
