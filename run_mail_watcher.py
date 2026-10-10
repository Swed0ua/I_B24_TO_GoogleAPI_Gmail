"""
Окремий сервіс: unread Gmail inbox → Telegram.
Не чіпає main.py / connect_to_gapi.py.

Запуск:
  python run_mail_watcher.py

Один раз отримати token.pickle:
  python -m mail_watcher.inbox
"""
from dotenv import load_dotenv

load_dotenv()

import logging

from mail_watcher.runner import run_mail_watcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

if __name__ == '__main__':
    run_mail_watcher()
