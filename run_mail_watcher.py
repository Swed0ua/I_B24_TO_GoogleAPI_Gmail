"""
Окремий процес: unread Gmail inbox → Telegram.
Стартує з main через spawn_mail_watcher_process() або вручну:

  python run_mail_watcher.py
  python -m mail_watcher.inbox   # один раз → token.pickle
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
