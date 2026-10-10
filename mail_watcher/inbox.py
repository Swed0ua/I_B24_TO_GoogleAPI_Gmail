from __future__ import annotations

import base64
import logging
import pickle
import re
from email.utils import parseaddr
from html.parser import HTMLParser
from typing import Iterable

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from mail_watcher.config import MailWatcherSettings
from mail_watcher.models import IncomingMail

logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
]


class _HtmlText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def text(self) -> str:
        return re.sub(r'\s+', ' ', ''.join(self._parts)).strip()


def get_service(settings: MailWatcherSettings):
    creds = None
    token_path = settings.token_path
    secret_path = settings.client_secret_path

    if token_path.is_file():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
            creds = flow.run_local_server(port=0)
        settings.secrets_dir.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds, cache_discovery=False)


def _b64(data: str) -> str:
    padded = data + '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode('utf-8', errors='replace')


def _headers(payload: dict) -> dict[str, str]:
    return {h['name'].lower(): h.get('value', '') for h in payload.get('headers', [])}


def _walk(payload: dict):
    yield payload
    for part in payload.get('parts') or []:
        yield from _walk(part)


def _body(payload: dict) -> str:
    plain, html = '', ''
    for part in _walk(payload):
        data = (part.get('body') or {}).get('data')
        if not data:
            continue
        mime = part.get('mimeType', '')
        text = _b64(data)
        if mime == 'text/plain' and not plain:
            plain = text.strip()
        elif mime == 'text/html' and not html:
            parser = _HtmlText()
            parser.feed(text)
            html = parser.text()
    return plain or html


def _attachments(payload: dict) -> tuple[str, ...]:
    return tuple(part['filename'] for part in _walk(payload) if part.get('filename'))


def _parse(msg: dict) -> IncomingMail:
    payload = msg.get('payload') or {}
    headers = _headers(payload)
    from_name, from_addr = parseaddr(headers.get('from', ''))
    return IncomingMail(
        uid=msg['id'],
        from_addr=from_addr.lower(),
        from_name=from_name,
        subject=headers.get('subject', '').strip(),
        date=headers.get('date', '').strip(),
        body=_body(payload),
        in_reply_to=headers.get('in-reply-to', '').strip(),
        references=headers.get('references', '').strip(),
        attachments=_attachments(payload),
    )


class GmailInbox:
    def __init__(self, settings: MailWatcherSettings) -> None:
        self._service = get_service(settings)

    def fetch_unseen(self) -> list[IncomingMail]:
        result = self._service.users().messages().list(
            userId='me',
            q='in:inbox is:unread',
            maxResults=50,
        ).execute()
        ids = [item['id'] for item in result.get('messages') or []]
        mails: list[IncomingMail] = []
        for msg_id in ids:
            raw = self._service.users().messages().get(
                userId='me', id=msg_id, format='full'
            ).execute()
            mails.append(_parse(raw))
        return mails

    def mark_seen(self, uids: Iterable[str]) -> None:
        for msg_id in uids:
            self._service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']},
            ).execute()


if __name__ == '__main__':
    from mail_watcher.config import load_settings

    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    get_service(settings)
    print('OK', settings.token_path)
