#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR / '.env'
VENV_PYTHON = APP_DIR / 'venv' / 'bin' / 'python'
SERVICE_NAME = 'hysteria-telegram-bot-v2.service'
SERVICE_FILE = Path('/etc/systemd/system') / SERVICE_NAME

def fail(msg: str, code: int = 1) -> None:
    print(msg)
    raise SystemExit(code)

def ensure_env() -> None:
    if not ENV_FILE.exists():
        fail(f'Missing {ENV_FILE}. Create it from .env.example first.')

def ensure_python() -> None:
    if not VENV_PYTHON.exists():
        fail(f'Missing venv python: {VENV_PYTHON}. Create venv and install requirements first.')

def write_service() -> None:
    content = f"""[Unit]
Description=Hysteria Telegram Bot v2
After=network.target

[Service]
WorkingDirectory={APP_DIR}
EnvironmentFile={ENV_FILE}
ExecStart={VENV_PYTHON} {APP_DIR / "tbot.py"}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    SERVICE_FILE.write_text(content)
    os.chmod(SERVICE_FILE, 0o644)

def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=check)

def start() -> None:
    ensure_env()
    ensure_python()
    write_service()
    run('systemctl', 'daemon-reload')
    run('systemctl', 'enable', SERVICE_NAME)
    run('systemctl', 'restart', SERVICE_NAME)
    print(run('systemctl', 'status', SERVICE_NAME, '--no-pager', check=False).stdout)

def stop() -> None:
    run('systemctl', 'stop', SERVICE_NAME, check=False)
    run('systemctl', 'disable', SERVICE_NAME, check=False)
    print('Stopped.')

def restart() -> None:
    run('systemctl', 'restart', SERVICE_NAME)
    print(run('systemctl', 'status', SERVICE_NAME, '--no-pager', check=False).stdout)

def status() -> None:
    print(run('systemctl', 'status', SERVICE_NAME, '--no-pager', check=False).stdout)

def set_backup_interval(value: str) -> None:
    ensure_env()
    lines = ENV_FILE.read_text().splitlines()
    out = []
    found = False
    for line in lines:
        if line.startswith('BACKUP_INTERVAL_HOUR='):
            out.append(f'BACKUP_INTERVAL_HOUR={value}')
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f'BACKUP_INTERVAL_HOUR={value}')
    ENV_FILE.write_text('\n'.join(out) + '\n')
    run('systemctl', 'restart', SERVICE_NAME, check=False)
    print(f'BACKUP_INTERVAL_HOUR={value}')

def usage() -> None:
    print('Usage: python3 runbot.py start|stop|restart|status|set-backup-interval <hours>')
    raise SystemExit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    cmd = sys.argv[1]
    if cmd == 'start':
        start()
    elif cmd == 'stop':
        stop()
    elif cmd == 'restart':
        restart()
    elif cmd == 'status':
        status()
    elif cmd == 'set-backup-interval' and len(sys.argv) == 3:
        set_backup_interval(sys.argv[2])
    else:
        usage()
