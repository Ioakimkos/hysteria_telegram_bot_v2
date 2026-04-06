from __future__ import annotations
from telebot import types

BTN_ADD_USER = '➕ Add User'
BTN_SHOW_USER = '🔍 Show User'
BTN_DELETE_USER = '🗑️ Delete User'
BTN_SERVER_INFO = '🖥️ Server Info'
BTN_BACKUP = '💾 Backup Server'
BTN_SETTINGS = '⚙️ Settings'
BTN_WEBPANEL_URL = '🔗 Get Webpanel URL'
BTN_DASHBOARD = '📊 Dashboard'
BTN_BACK = '⬅️ Back'
BTN_CANCEL = '❌ Cancel'
BTN_SKIP = '⏭️ Skip'

MAX_MESSAGE = 3500

def create_main_markup():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(BTN_ADD_USER, BTN_SHOW_USER)
    m.row(BTN_DELETE_USER, BTN_SERVER_INFO)
    m.row(BTN_BACKUP, BTN_DASHBOARD)
    m.row(BTN_SETTINGS)
    return m

def create_settings_markup():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(BTN_WEBPANEL_URL)
    m.row(BTN_BACK)
    return m

def create_cancel_markup(back=False):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if back:
        m.row(BTN_BACK)
    m.row(BTN_CANCEL)
    return m

def create_cancel_markup_with_skip(back=False):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if back:
        m.row(BTN_BACK)
    m.row(BTN_SKIP, BTN_CANCEL)
    return m

def user_actions_markup(username: str, blocked: bool | None = None):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton('🔄 Reset', callback_data=f'reset:{username}'),
        types.InlineKeyboardButton('🌐 IPv6 URI', callback_data=f'ipv6:{username}')
    )
    m.add(
        types.InlineKeyboardButton('✏️ Edit Traffic', callback_data=f'edit_traffic:{username}'),
        types.InlineKeyboardButton('📅 Edit Expiration', callback_data=f'edit_days:{username}')
    )
    m.add(
        types.InlineKeyboardButton('🔑 Renew Password', callback_data=f'renew_password:{username}'),
        types.InlineKeyboardButton('🕒 Renew Creation', callback_data=f'renew_creation:{username}')
    )
    label = '✅ Unblock' if blocked else '⛔ Block'
    action = 'unblock' if blocked else 'block'
    m.add(types.InlineKeyboardButton(label, callback_data=f'{action}:{username}'))
    return m

def dashboard_markup():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton('🔄 Refresh Dashboard', callback_data='dashboard_refresh'))
    return m

def escape_md(text: str) -> str:
    return str(text).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

def split_message(text: str) -> list[str]:
    if len(text) <= MAX_MESSAGE:
        return [text]
    parts = []
    current = ''
    for line in text.splitlines(True):
        if len(current) + len(line) > MAX_MESSAGE:
            parts.append(current)
            current = line
        else:
            current += line
    if current:
        parts.append(current)
    return parts
