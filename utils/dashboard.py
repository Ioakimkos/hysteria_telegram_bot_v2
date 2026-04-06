from __future__ import annotations
import json
from .actions import list_users_json, traffic_status_text, server_info_text

def build_dashboard_text() -> str:
    users = list_users_json()
    total_users = len(users)
    blocked_users = sum(1 for u in users if u.get('blocked'))
    online_like = sum(1 for u in users if u.get('status') in ('online', 'active', True))

    total_limit_bytes = sum(int(u.get('max_download_bytes') or 0) for u in users)
    total_limit_gb = total_limit_bytes / (1024 ** 3)

    traffic = traffic_status_text()
    server = server_info_text()

    lines = [
        '📊 *Hysteria Dashboard*',
        '',
        f'👥 Users: *{total_users}*',
        f'🚫 Blocked: *{blocked_users}*',
        f'🟢 Active/Online-like: *{online_like}*',
        f'📦 Total traffic limit: *{total_limit_gb:.2f} GB*',
        '',
        '*Traffic Status*',
        '```',
        (traffic[:1200] if traffic else 'No data'),
        '```',
        '',
        '*Server Info*',
        '```',
        (server[:1200] if server else 'No data'),
        '```',
    ]
    return '\n'.join(lines)
