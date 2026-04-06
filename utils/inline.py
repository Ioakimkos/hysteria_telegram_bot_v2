from __future__ import annotations
from telebot import types
from .command import bot, is_admin
from .actions import list_users_json

def register_inline_handlers():
    @bot.inline_handler(lambda q: is_admin(q.from_user.id))
    def inline_users(query):
        users = list_users_json()
        q = (query.query or '').lower()
        results = []
        for user in users:
            username = user.get('username', '')
            if q and q not in username.lower() and not (q == 'block' and user.get('blocked')):
                continue
            desc = f"Traffic Limit: {user.get('max_download_bytes', 0) / (1024 ** 3):.2f} GB, Expiration Days: {user.get('expiration_days', 'N/A')}"
            text = (
                f"Name: {username}\n"
                f"Traffic limit: {user.get('max_download_bytes', 0) / (1024 ** 3):.2f} GB\n"
                f"Days: {user.get('expiration_days', 'N/A')}\n"
                f"Account Creation: {user.get('account_creation_date', 'N/A')}\n"
                f"Blocked: {user.get('blocked', False)}"
            )
            results.append(types.InlineQueryResultArticle(
                id=username,
                title=(username + (' (Blocked)' if user.get('blocked') else '')),
                description=desc,
                input_message_content=types.InputTextMessageContent(message_text=text)
            ))
        bot.answer_inline_query(query.id, results[:20], cache_time=1)
