from __future__ import annotations

import logging
import subprocess
from typing import Sequence
import telebot

from .config import settings

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(settings.api_token, parse_mode='Markdown')

def is_admin(user_id: int) -> bool:
    return int(user_id) in settings.admin_user_ids

def run_cli_command(args: Sequence[str]) -> str:
    try:
        result = subprocess.run(
            list(args),
            capture_output=True,
            text=True,
            timeout=settings.command_timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 'Error: command timed out'
    except Exception as e:
        logger.exception('Failed to execute command')
        return f'Error: {e}'

    output = (result.stdout or '').strip()
    error = (result.stderr or '').strip()

    if result.returncode != 0:
        if error:
            return f'Error:\n{error}'
        if output:
            return f'Error:\n{output}'
        return f'Error: exit code {result.returncode}'
    return output or 'OK'
