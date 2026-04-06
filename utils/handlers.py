from __future__ import annotations

import io
import json
import logging
import qrcode
import re
from telebot import types

from .actions import (
    add_user_text,
    backup_hysteria,
    get_user_text,
    get_webpanel_url_text,
    latest_backup_path,
    remove_user_text,
    server_info_text,
    show_user_uri_text,
)
from .command import bot, is_admin
from .common import (
    BTN_ADD_USER, BTN_BACK, BTN_BACKUP, BTN_CANCEL, BTN_DELETE_USER, BTN_SERVER_INFO,
    BTN_SETTINGS, BTN_SHOW_USER, BTN_SKIP, BTN_WEBPANEL_URL,
    create_cancel_markup, create_cancel_markup_with_skip, create_main_markup,
    create_settings_markup, escape_md, split_message
)

logger = logging.getLogger(__name__)
_state: dict[int, dict] = {}

def _deny(message):
    bot.reply_to(message, 'Unauthorized access.')

def _state_set(chat_id: int, **kwargs):
    _state[chat_id] = kwargs

def _state_get(chat_id: int):
    return _state.get(chat_id, {})

def _state_clear(chat_id: int):
    _state.pop(chat_id, None)

def _send_long(chat_id: int, text: str, **kwargs):
    for part in split_message(text):
        bot.send_message(chat_id, part, **kwargs)

def register_handlers():
    @bot.message_handler(commands=['start'])
    def start(message):
        if not is_admin(message.from_user.id):
            return _deny(message)
        bot.reply_to(message, 'Welcome to the User Management Bot!', reply_markup=create_main_markup())

    @bot.message_handler(commands=['system'])
    def system_info(message):
        if not is_admin(message.from_user.id):
            return _deny(message)
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        bot.reply_to(message, f'📊 System Resource Usage\n\n📈 CPU Usage: {cpu:.1f}%\n📋 RAM Usage: {ram:.1f}%')

    @bot.message_handler(func=lambda m: True)
    def route(message):
        if not is_admin(message.from_user.id):
            return _deny(message)

        text = (message.text or '').strip()
        state = _state_get(message.chat.id)

        if text == BTN_SERVER_INFO:
            return _send_long(message.chat.id, server_info_text(), reply_markup=create_main_markup())
        if text == BTN_SETTINGS:
            return bot.send_message(message.chat.id, '⚙️ Settings Menu:', reply_markup=create_settings_markup())
        if text == BTN_BACK:
            _state_clear(message.chat.id)
            return bot.send_message(message.chat.id, '⬅️ Returning to Main Menu...', reply_markup=create_main_markup())
        if text == BTN_WEBPANEL_URL:
            return bot.reply_to(message, '🌐 Webpanel URL:\n' + get_webpanel_url_text(), reply_markup=create_settings_markup())
        if text == BTN_BACKUP:
            bot.reply_to(message, 'Starting backup. This may take a few moments...')
            result = backup_hysteria()
            if result.startswith('Error'):
                return bot.reply_to(message, result, reply_markup=create_main_markup())
            backup = latest_backup_path()
            if not backup:
                return bot.reply_to(message, 'No backup file found after the backup process.', reply_markup=create_main_markup())
            with open(backup, 'rb') as f:
                return bot.send_document(message.chat.id, f, caption=f'Manual backup completed: {backup.split("/")[-1]}')
        if text == BTN_DELETE_USER:
            _state_set(message.chat.id, mode='delete_user')
            return bot.reply_to(message, 'Enter username:', reply_markup=create_cancel_markup())
        if text == BTN_SHOW_USER:
            _state_set(message.chat.id, mode='show_user')
            return bot.reply_to(message, 'Enter username:', reply_markup=create_cancel_markup())
        if text == BTN_ADD_USER:
            _state_set(message.chat.id, mode='add_user_username')
            return bot.reply_to(message, 'Enter username (letters, numbers, underscores only):', reply_markup=create_cancel_markup())

        if text == BTN_CANCEL:
            _state_clear(message.chat.id)
            return bot.reply_to(message, 'Process canceled.', reply_markup=create_main_markup())

        mode = state.get('mode')
        if mode == 'delete_user':
            _state_clear(message.chat.id)
            return bot.reply_to(message, remove_user_text(text.strip().lower()), reply_markup=create_main_markup())

        if mode == 'show_user':
            _state_clear(message.chat.id)
            username = text.strip()
            user_json = get_user_text(username)
            if user_json.startswith('Error'):
                return bot.reply_to(message, user_json, reply_markup=create_main_markup())
            try:
                data = json.loads(user_json)
            except Exception:
                return bot.reply_to(message, user_json, reply_markup=create_main_markup())
            details = (
                f"🆔 Name: {escape_md(data.get('username', username))}\n"
                f"📊 Traffic Limit: {data.get('max_download_bytes', 0) / (1024 ** 3):.2f} GB\n"
                f"📅 Days: {data.get('expiration_days', 'N/A')}\n"
                f"⏳ Creation: {data.get('account_creation_date', 'N/A')}\n"
                f"💡 Blocked: {data.get('blocked', 'N/A')}\n"
            )
            uri = show_user_uri_text(username, 4)
            qr_link = None
            for line in uri.splitlines():
                line = line.strip()
                if line.startswith('hy2://') or line.startswith('http://') or line.startswith('https://'):
                    qr_link = line
                    break
            if qr_link:
                img = qrcode.make(qr_link)
                bio = io.BytesIO()
                img.save(bio, 'PNG')
                bio.seek(0)
                return bot.send_photo(message.chat.id, bio, caption=details, reply_markup=create_main_markup())
            return bot.reply_to(message, details, reply_markup=create_main_markup())

        if mode == 'add_user_username':
            username = text.strip()
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return bot.reply_to(message, 'Invalid username. Only letters, numbers, and underscores are allowed.', reply_markup=create_cancel_markup())
            _state_set(message.chat.id, mode='add_user_traffic', username=username)
            return bot.reply_to(message, 'Enter traffic limit (GB):', reply_markup=create_cancel_markup(back=True))

        if mode == 'add_user_traffic':
            if text == BTN_BACK:
                _state_set(message.chat.id, mode='add_user_username')
                return bot.reply_to(message, 'Enter username:', reply_markup=create_cancel_markup())
            try:
                traffic = int(text)
                if traffic < 0:
                    raise ValueError
            except Exception:
                return bot.reply_to(message, 'Invalid traffic limit. Enter a non-negative integer.', reply_markup=create_cancel_markup(back=True))
            state['traffic'] = traffic
            _state_set(message.chat.id, **state, mode='add_user_days')
            return bot.reply_to(message, 'Enter expiration days:', reply_markup=create_cancel_markup(back=True))

        if mode == 'add_user_days':
            if text == BTN_BACK:
                _state_set(message.chat.id, **state, mode='add_user_traffic')
                return bot.reply_to(message, 'Enter traffic limit (GB):', reply_markup=create_cancel_markup(back=True))
            try:
                days = int(text)
                if days < 0:
                    raise ValueError
            except Exception:
                return bot.reply_to(message, 'Invalid expiration days. Enter a non-negative integer.', reply_markup=create_cancel_markup(back=True))
            state['days'] = days
            _state_set(message.chat.id, **state, mode='add_user_note')
            return bot.reply_to(message, 'Enter note (optional, or Skip):', reply_markup=create_cancel_markup_with_skip(back=True))

        if mode == 'add_user_note':
            if text == BTN_BACK:
                _state_set(message.chat.id, **state, mode='add_user_days')
                return bot.reply_to(message, 'Enter expiration days:', reply_markup=create_cancel_markup(back=True))
            note = None if text == BTN_SKIP else text.strip()
            result = add_user_text(state['username'], state['traffic'], state['days'], note)
            _state_clear(message.chat.id)
            return bot.reply_to(message, result, reply_markup=create_main_markup())

        return bot.send_message(message.chat.id, 'Use the menu buttons.', reply_markup=create_main_markup())
