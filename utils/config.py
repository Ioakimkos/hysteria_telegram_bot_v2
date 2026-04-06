from __future__ import annotations
import json, os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    api_token: str
    admin_user_ids: list[int]
    cli_path: str
    backup_directory: str
    backup_interval_hour: int
    cpu_alert_threshold: float
    ram_alert_threshold: float
    command_timeout: int
    log_level: str

def req(name: str) -> str:
    v = os.getenv(name, '').strip()
    if not v:
        raise RuntimeError(f'Missing required env: {name}')
    return v

settings = Settings(
    api_token=req('API_TOKEN'),
    admin_user_ids=[int(x) for x in json.loads(req('ADMIN_USER_IDS'))],
    cli_path=os.getenv('CLI_PATH', '/etc/hysteria/core/cli.py'),
    backup_directory=os.getenv('BACKUP_DIRECTORY', '/opt/hysbackup'),
    backup_interval_hour=int(os.getenv('BACKUP_INTERVAL_HOUR', '12')),
    cpu_alert_threshold=float(os.getenv('CPU_ALERT_THRESHOLD', '90')),
    ram_alert_threshold=float(os.getenv('RAM_ALERT_THRESHOLD', '90')),
    command_timeout=int(os.getenv('COMMAND_TIMEOUT', '30')),
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
)
