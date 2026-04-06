from __future__ import annotations

from telebot import types

MAX_MESSAGE = 3500

BTN_ADD_USER = '➕ Add User'
BTN_SHOW_USER = '🔍 Show User'
BTN_DELETE_USER = '🗑️ Delete User'
BTN_SERVER_INFO = '🖥️ Server Info'
BTN_BACKUP = '💾 Backup Server'
BTN_SETTINGS = '⚙️ Settings'
BTN_WEBPANEL_URL = '🔗 Get Webpanel URL'
BTN_BACK = '⬅️ Back'
BTN_CANCEL = '❌ Cancel'
BTN_SKIP = '⏭️ Skip'

def create_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BTN_ADD_USER, BTN_SHOW_USER)
    markup.row(BTN_DELETE_USER, BTN_SERVER_INFO)
    markup.row(BTN_BACKUP, BTN_SETTINGS)
    return markup

def create_settings_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BTN_WEBPANEL_URL)
    markup.row(BTN_BACK)
    return markup

def create_cancel_markup(back: bool = False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if back:
        markup.row(types.KeyboardButton(BTN_BACK))
    markup.row(types.KeyboardButton(BTN_CANCEL))
    return markup

def create_cancel_markup_with_skip(back: bool = False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if back:
        markup.row(types.KeyboardButton(BTN_BACK))
    markup.row(types.KeyboardButton(BTN_SKIP), types.KeyboardButton(BTN_CANCEL))
    return markup

def escape_md(text: str) -> str:
    return str(text).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

def split_message(text: str) -> list[str]:
    if len(text) <= MAX_MESSAGE:
        return [text]
    parts = []
    current = []
    size = 0
    for line in text.splitlines(True):
        if size + len(line) > MAX_MESSAGE and current:
            parts.append(''.join(current))
            current = [line]
            size = len(line)
        else:
            current.append(line)
            size += len(line)
    if current:
        parts.append(''.join(current))
    return parts
