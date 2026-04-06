from __future__ import annotations
import io, qrcode, re
from telebot import types

from .actions import (
    add_user_text, backup_hysteria, block_user_text, edit_user_days_text,
    edit_user_traffic_text, get_user_json, get_webpanel_url_text, latest_backup_path,
    remove_user_text, renew_creation_text, renew_password_text, reset_user_text,
    server_info_text, show_user_uri_text, unblock_user_text
)
from .command import bot, is_admin
from .common import (
    BTN_ADD_USER, BTN_BACK, BTN_BACKUP, BTN_CANCEL, BTN_DASHBOARD, BTN_DELETE_USER,
    BTN_SERVER_INFO, BTN_SETTINGS, BTN_SHOW_USER, BTN_SKIP, BTN_WEBPANEL_URL,
    create_cancel_markup, create_cancel_markup_with_skip, create_main_markup,
    create_settings_markup, dashboard_markup, escape_md, split_message, user_actions_markup
)
from .dashboard import build_dashboard_text
from .inline import register_inline_handlers

_state = {}

def _deny(message):
    bot.reply_to(message, 'Unauthorized access.')

def _set(chat_id: int, **kwargs):
    _state[chat_id] = kwargs

def _get(chat_id: int):
    return _state.get(chat_id, {})

def _clear(chat_id: int):
    _state.pop(chat_id, None)

def _send_long(chat_id: int, text: str, **kwargs):
    for part in split_message(text):
        bot.send_message(chat_id, part, **kwargs)

def _send_user_card(chat_id: int, username: str):
    data = get_user_json(username)
    if not data:
        return bot.send_message(chat_id, f'User `{escape_md(username)}` not found.', reply_markup=create_main_markup())
    details = (
        f"🆔 Name: {escape_md(data.get('username', username))}\n"
        f"📊 Traffic Limit: {data.get('max_download_bytes', 0) / (1024 ** 3):.2f} GB\n"
        f"📅 Days: {data.get('expiration_days', 'N/A')}\n"
        f"⏳ Creation: {data.get('account_creation_date', 'N/A')}\n"
        f"💡 Blocked: {data.get('blocked', 'N/A')}\n"
        f"📝 Note: {escape_md(data.get('note', '') or 'None')}"
    )
    uri_text = show_user_uri_text(username, 4)
    qr_link = None
    for line in uri_text.splitlines():
        s = line.strip()
        if s.startswith('hy2://') or s.startswith('http://') or s.startswith('https://'):
            qr_link = s
            break
    blocked = bool(data.get('blocked'))
    if qr_link:
        img = qrcode.make(qr_link)
        bio = io.BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        return bot.send_photo(chat_id, bio, caption=details, reply_markup=user_actions_markup(username, blocked))
    return bot.send_message(chat_id, details, reply_markup=user_actions_markup(username, blocked))

def register_handlers():
    register_inline_handlers()

    @bot.message_handler(commands=['start'])
    def start(message):
        if not is_admin(message.from_user.id):
            return _deny(message)
        bot.reply_to(message, 'Welcome to the User Management Bot!', reply_markup=create_main_markup())

    @bot.message_handler(commands=['system'])
    def system(message):
        if not is_admin(message.from_user.id):
            return _deny(message)
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        bot.reply_to(message, f'📊 System Resource Usage\n\n📈 CPU Usage: {cpu:.1f}%\n📋 RAM Usage: {ram:.1f}%')

    @bot.callback_query_handler(func=lambda c: True)
    def callbacks(call):
        if not is_admin(call.from_user.id):
            return
        data = call.data or ''
        if data == 'dashboard_refresh':
            return bot.edit_message_text(build_dashboard_text(), call.message.chat.id, call.message.message_id, reply_markup=dashboard_markup())
        if ':' not in data:
            return
        action, username = data.split(':', 1)
        if action == 'reset':
            res = reset_user_text(username)
            bot.answer_callback_query(call.id, 'Reset done')
            return bot.send_message(call.message.chat.id, res, reply_markup=create_main_markup())
        if action == 'ipv6':
            res = show_user_uri_text(username, 6)
            return _send_long(call.message.chat.id, res, reply_markup=create_main_markup())
        if action == 'renew_password':
            res = renew_password_text(username)
            bot.answer_callback_query(call.id, 'Password renewed')
            return bot.send_message(call.message.chat.id, res, reply_markup=create_main_markup())
        if action == 'renew_creation':
            res = renew_creation_text(username)
            bot.answer_callback_query(call.id, 'Creation renewed')
            return bot.send_message(call.message.chat.id, res, reply_markup=create_main_markup())
        if action == 'block':
            res = block_user_text(username)
            bot.answer_callback_query(call.id, 'Blocked')
            return bot.send_message(call.message.chat.id, res, reply_markup=create_main_markup())
        if action == 'unblock':
            res = unblock_user_text(username)
            bot.answer_callback_query(call.id, 'Unblocked')
            return bot.send_message(call.message.chat.id, res, reply_markup=create_main_markup())
        if action == 'edit_traffic':
            _set(call.message.chat.id, mode='edit_traffic', username=username)
            bot.answer_callback_query(call.id)
            return bot.send_message(call.message.chat.id, f'Enter new traffic limit (GB) for `{escape_md(username)}`:', reply_markup=create_cancel_markup(), parse_mode='Markdown')
        if action == 'edit_days':
            _set(call.message.chat.id, mode='edit_days', username=username)
            bot.answer_callback_query(call.id)
            return bot.send_message(call.message.chat.id, f'Enter new expiration days for `{escape_md(username)}`:', reply_markup=create_cancel_markup(), parse_mode='Markdown')

    @bot.message_handler(func=lambda m: True)
    def route(message):
        if not is_admin(message.from_user.id):
            return _deny(message)

        text = (message.text or '').strip()
        state = _get(message.chat.id)
        mode = state.get('mode')

        if text == BTN_SERVER_INFO:
            return _send_long(message.chat.id, server_info_text(), reply_markup=create_main_markup())
        if text == BTN_DASHBOARD:
            return bot.send_message(message.chat.id, build_dashboard_text(), reply_markup=dashboard_markup())
        if text == BTN_SETTINGS:
            return bot.send_message(message.chat.id, '⚙️ Settings Menu:', reply_markup=create_settings_markup())
        if text == BTN_BACK:
            _clear(message.chat.id)
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
            _set(message.chat.id, mode='delete_user')
            return bot.reply_to(message, 'Enter username:', reply_markup=create_cancel_markup())
        if text == BTN_SHOW_USER:
            _set(message.chat.id, mode='show_user')
            return bot.reply_to(message, 'Enter username:', reply_markup=create_cancel_markup())
        if text == BTN_ADD_USER:
            _set(message.chat.id, mode='add_user_username')
            return bot.reply_to(message, 'Enter username (letters, numbers, underscores only):', reply_markup=create_cancel_markup())

        if text == BTN_CANCEL:
            _clear(message.chat.id)
            return bot.reply_to(message, 'Process canceled.', reply_markup=create_main_markup())

        if mode == 'delete_user':
            _clear(message.chat.id)
            return bot.reply_to(message, remove_user_text(text.strip().lower()), reply_markup=create_main_markup())

        if mode == 'show_user':
            _clear(message.chat.id)
            return _send_user_card(message.chat.id, text.strip())

        if mode == 'edit_traffic':
            try:
                traffic = int(text)
                if traffic < 0:
                    raise ValueError
            except Exception:
                return bot.reply_to(message, 'Invalid traffic limit. Enter a non-negative integer.', reply_markup=create_cancel_markup())
            res = edit_user_traffic_text(state['username'], traffic)
            _clear(message.chat.id)
            return bot.reply_to(message, res, reply_markup=create_main_markup())

        if mode == 'edit_days':
            try:
                days = int(text)
                if days < 0:
                    raise ValueError
            except Exception:
                return bot.reply_to(message, 'Invalid expiration days. Enter a non-negative integer.', reply_markup=create_cancel_markup())
            res = edit_user_days_text(state['username'], days)
            _clear(message.chat.id)
            return bot.reply_to(message, res, reply_markup=create_main_markup())

        if mode == 'add_user_username':
            username = text.strip()
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return bot.reply_to(message, 'Invalid username. Only letters, numbers, and underscores are allowed.', reply_markup=create_cancel_markup())
            _set(message.chat.id, mode='add_user_traffic', username=username)
            return bot.reply_to(message, 'Enter traffic limit (GB):', reply_markup=create_cancel_markup(back=True))

        if mode == 'add_user_traffic':
            if text == BTN_BACK:
                _set(message.chat.id, mode='add_user_username')
                return bot.reply_to(message, 'Enter username:', reply_markup=create_cancel_markup())
            try:
                traffic = int(text)
                if traffic < 0:
                    raise ValueError
            except Exception:
                return bot.reply_to(message, 'Invalid traffic limit. Enter a non-negative integer.', reply_markup=create_cancel_markup(back=True))
            state['traffic'] = traffic
            _set(message.chat.id, **state, mode='add_user_days')
            return bot.reply_to(message, 'Enter expiration days:', reply_markup=create_cancel_markup(back=True))

        if mode == 'add_user_days':
            if text == BTN_BACK:
                _set(message.chat.id, **state, mode='add_user_traffic')
                return bot.reply_to(message, 'Enter traffic limit (GB):', reply_markup=create_cancel_markup(back=True))
            try:
                days = int(text)
                if days < 0:
                    raise ValueError
            except Exception:
                return bot.reply_to(message, 'Invalid expiration days. Enter a non-negative integer.', reply_markup=create_cancel_markup(back=True))
            state['days'] = days
            _set(message.chat.id, **state, mode='add_user_note')
            return bot.reply_to(message, 'Enter note (optional, or Skip):', reply_markup=create_cancel_markup_with_skip(back=True))

        if mode == 'add_user_note':
            if text == BTN_BACK:
                _set(message.chat.id, **state, mode='add_user_days')
                return bot.reply_to(message, 'Enter expiration days:', reply_markup=create_cancel_markup(back=True))
            note = None if text == BTN_SKIP else text.strip()
            result = add_user_text(state['username'], state['traffic'], state['days'], note)
            _clear(message.chat.id)
            return bot.reply_to(message, result, reply_markup=create_main_markup())

        return bot.send_message(message.chat.id, 'Use the menu buttons.', reply_markup=create_main_markup())
