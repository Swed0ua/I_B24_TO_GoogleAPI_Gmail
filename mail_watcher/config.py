from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_SECRETS = Path(__file__).resolve().parent / 'secrets'


@dataclass(frozen=True)
class MailWatcherSettings:
    enabled: bool
    poll_interval_sec: int
    skip_domains: tuple[str, ...]
    telegram_bot_token: str
    telegram_chat_ids: tuple[str, ...]
    secrets_dir: Path
    client_secret_path: Path
    token_path: Path

    @property
    def ready(self) -> bool:
        return self.client_secret_path.is_file() and self.token_path.is_file()


def _parse_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part.strip() for part in value.split(',') if part.strip())


def load_settings() -> MailWatcherSettings:
    secrets_raw = os.getenv('GMAIL_SECRETS_DIR', '').strip()
    secrets_dir = Path(secrets_raw) if secrets_raw else _DEFAULT_SECRETS
    if not secrets_dir.is_absolute():
        secrets_dir = _ROOT / secrets_dir

    return MailWatcherSettings(
        enabled=_parse_bool(os.getenv('MAIL_WATCHER_ENABLED'), True),
        poll_interval_sec=max(1, int(os.getenv('MAIL_POLL_INTERVAL_SEC', '60'))),
        skip_domains=_csv(os.getenv('MAIL_SKIP_DOMAINS', 'google.com,googlemail.com')),
        telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN', '').strip(),
        telegram_chat_ids=_csv(os.getenv('TELEGRAM_CHAT_IDS')),
        secrets_dir=secrets_dir,
        client_secret_path=secrets_dir / 'client_secret.json',
        token_path=secrets_dir / 'token.pickle',
    )
