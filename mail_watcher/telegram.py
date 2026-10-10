import logging

import requests

from mail_watcher.config import MailWatcherSettings
from mail_watcher.models import IncomingMail

logger = logging.getLogger(__name__)

_API = 'https://api.telegram.org/bot{token}/sendMessage'
_BODY_LIMIT = 3000


class TelegramNotifier:
    def __init__(self, settings: MailWatcherSettings) -> None:
        self._s = settings

    @property
    def enabled(self) -> bool:
        return bool(self._s.telegram_bot_token and self._s.telegram_chat_ids)

    def send_mail(self, mail: IncomingMail) -> None:
        if not self.enabled:
            logger.warning('Telegram is not configured, skip notify for uid %s', mail.uid)
            return
        text = self._format(mail)
        for chat_id in self._s.telegram_chat_ids:
            self._post(chat_id, text)

    def _post(self, chat_id: str, text: str) -> None:
        url = _API.format(token=self._s.telegram_bot_token)
        response = requests.post(
            url,
            json={'chat_id': chat_id, 'text': text, 'disable_web_page_preview': True},
            timeout=20,
        )
        if not response.ok:
            raise RuntimeError(f'Telegram {response.status_code}: {response.text}')

    @staticmethod
    def _format(mail: IncomingMail) -> str:
        body = mail.body.strip() or '(empty body)'
        if len(body) > _BODY_LIMIT:
            body = body[:_BODY_LIMIT] + '\n…'
        lines = [
            'New mail',
            f'From: {mail.from_name} <{mail.from_addr}>'.strip(),
            f'Subject: {mail.subject or "(no subject)"}',
            f'Date: {mail.date or "-"}',
        ]
        if mail.attachments:
            lines.append('Files: ' + ', '.join(mail.attachments))
        lines.extend(['', body])
        return '\n'.join(lines)
