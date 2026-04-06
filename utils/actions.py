from __future__ import annotations

import json
import os
from pathlib import Path

from .command import run_cli_command
from .config import settings

CLI = ['python3', settings.cli_path]

def list_users_text() -> str:
    return run_cli_command([*CLI, 'list-users'])

def server_info_text() -> str:
    return run_cli_command([*CLI, 'server-info'])

def backup_hysteria() -> str:
    return run_cli_command([*CLI, 'backup-hysteria'])

def latest_backup_path() -> str | None:
    backup_dir = Path(settings.backup_directory)
    if not backup_dir.exists():
        return None
    files = sorted(
        [p for p in backup_dir.iterdir() if p.suffix == '.zip'],
        key=lambda p: p.stat().st_ctime,
        reverse=True,
    )
    return str(files[0]) if files else None

def get_user_text(username: str) -> str:
    return run_cli_command([*CLI, 'get-user', '-u', username])

def remove_user_text(username: str) -> str:
    return run_cli_command([*CLI, 'remove-user', username])

def add_user_text(username: str, traffic_limit: int, expiration_days: int, note: str | None = None) -> str:
    args = [*CLI, 'add-user', '-u', username, '-t', str(traffic_limit), '-e', str(expiration_days)]
    if note:
        args += ['-n', note]
    return run_cli_command(args)

def show_user_uri_text(username: str, ipv: int = 4) -> str:
    return run_cli_command([*CLI, 'show-user-uri', '-u', username, '-ip', str(ipv), '-n', '-s'])

def get_webpanel_url_text() -> str:
    status = run_cli_command([*CLI, 'get-webpanel-services-status'])
    if 'Inactive' in status:
        return '⚠️ The Webpanel service is currently inactive.'
    return run_cli_command([*CLI, 'get-webpanel-url', '--url-only'])

def check_version_text() -> str:
    return run_cli_command([*CLI, 'check-version'])
