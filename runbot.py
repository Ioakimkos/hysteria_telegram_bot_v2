#!/usr/bin/env python3
from __future__ import annotations
import sys, os, subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR / '.env'
VENV_PYTHON = APP_DIR / 'venv' / 'bin' / 'python'
SERVICE_NAME = 'hysteria-telegram-bot-v2_2.service'
SERVICE_FILE = Path('/etc/systemd/system') / SERVICE_NAME

def die(msg: str) -> None:
    print(msg)
    raise SystemExit(1)

def run(*args: str, check: bool = True):
    return subprocess.run(args, text=True, capture_output=True, check=check)

def write_service():
    SERVICE_FILE.write_text(f"""[Unit]
Description=Hysteria Telegram Bot v2.2
After=network.target

[Service]
WorkingDirectory={APP_DIR}
EnvironmentFile={ENV_FILE}
ExecStart={VENV_PYTHON} {APP_DIR / 'tbot.py'}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
""")

def start():
    if not ENV_FILE.exists():
        die(f'Missing {ENV_FILE}')
    if not VENV_PYTHON.exists():
        die(f'Missing {VENV_PYTHON}')
    write_service()
    run('systemctl', 'daemon-reload')
    run('systemctl', 'enable', SERVICE_NAME)
    run('systemctl', 'restart', SERVICE_NAME)
    print(run('systemctl', 'status', SERVICE_NAME, '--no-pager', check=False).stdout)

def stop():
    run('systemctl', 'stop', SERVICE_NAME, check=False)
    run('systemctl', 'disable', SERVICE_NAME, check=False)
    print('Stopped')

def restart():
    run('systemctl', 'restart', SERVICE_NAME)
    print(run('systemctl', 'status', SERVICE_NAME, '--no-pager', check=False).stdout)

def status():
    print(run('systemctl', 'status', SERVICE_NAME, '--no-pager', check=False).stdout)

def usage():
    print('Usage: python3 runbot.py start|stop|restart|status')
    raise SystemExit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    {'start': start, 'stop': stop, 'restart': restart, 'status': status}.get(sys.argv[1], usage)()
