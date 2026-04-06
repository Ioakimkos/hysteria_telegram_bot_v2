from __future__ import annotations
import json
from pathlib import Path
from .command import run_cli_command
from .config import settings

CLI = ['python3', settings.cli_path]

def list_users_text() -> str:
    return run_cli_command([*CLI, 'list-users'])

def list_users_json() -> list[dict]:
    raw = list_users_text()
    if raw.startswith('Error'):
        return []
    try:
        return json.loads(raw)
    except Exception:
        return []

def get_user_json(username: str) -> dict | None:
    raw = run_cli_command([*CLI, 'get-user', '-u', username])
    if raw.startswith('Error'):
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None

def server_info_text() -> str:
    return run_cli_command([*CLI, 'server-info'])

def traffic_status_text() -> str:
    return run_cli_command([*CLI, 'traffic-status', '--no-gui'])

def backup_hysteria() -> str:
    return run_cli_command([*CLI, 'backup-hysteria'])

def latest_backup_path() -> str | None:
    p = Path(settings.backup_directory)
    if not p.exists():
        return None
    files = sorted([x for x in p.iterdir() if x.suffix == '.zip'], key=lambda x: x.stat().st_ctime, reverse=True)
    return str(files[0]) if files else None

def add_user_text(username: str, traffic_limit: int, expiration_days: int, note: str | None = None) -> str:
    args = [*CLI, 'add-user', '-u', username, '-t', str(traffic_limit), '-e', str(expiration_days)]
    if note:
        args += ['-n', note]
    return run_cli_command(args)

def remove_user_text(username: str) -> str:
    return run_cli_command([*CLI, 'remove-user', username])

def show_user_uri_text(username: str, ipv: int = 4) -> str:
    return run_cli_command([*CLI, 'show-user-uri', '-u', username, '-ip', str(ipv), '-n', '-s'])

def edit_user_traffic_text(username: str, traffic: int) -> str:
    return run_cli_command([*CLI, 'edit-user', '-u', username, '-nt', str(traffic)])

def edit_user_days_text(username: str, days: int) -> str:
    return run_cli_command([*CLI, 'edit-user', '-u', username, '-ne', str(days)])

def reset_user_text(username: str) -> str:
    return run_cli_command([*CLI, 'reset-user', '-u', username])

def renew_password_text(username: str) -> str:
    return run_cli_command([*CLI, 'edit-user', '-u', username, '-rp'])

def renew_creation_text(username: str) -> str:
    return run_cli_command([*CLI, 'edit-user', '-u', username, '-rc'])

def block_user_text(username: str) -> str:
    return run_cli_command([*CLI, 'edit-user', '-u', username, '--blocked'])

def unblock_user_text(username: str) -> str:
    return run_cli_command([*CLI, 'edit-user', '-u', username, '--unblocked'])

def get_webpanel_url_text() -> str:
    status = run_cli_command([*CLI, 'get-webpanel-services-status'])
    if 'Inactive' in status:
        return '⚠️ The Webpanel service is currently inactive.'
    return run_cli_command([*CLI, 'get-webpanel-url', '--url-only'])

def check_version_text() -> str:
    return run_cli_command([*CLI, 'check-version'])
