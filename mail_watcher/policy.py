import re

from mail_watcher.config import MailWatcherSettings
from mail_watcher.models import IncomingMail

_REPLY_SUBJECT = re.compile(r'^(re|fw|fwd|відп)\s*(\[\d+\])?\s*:', re.IGNORECASE)


def is_reply(mail: IncomingMail) -> bool:
    if mail.in_reply_to or mail.references:
        return True
    return bool(_REPLY_SUBJECT.match(mail.subject.strip()))


def sender_domain(addr: str) -> str:
    if '@' not in addr:
        return ''
    return addr.rsplit('@', 1)[1].lower()


def is_skipped_sender(mail: IncomingMail, settings: MailWatcherSettings) -> bool:
    domain = sender_domain(mail.from_addr)
    if not domain:
        return False
    for skipped in settings.skip_domains:
        if domain == skipped or domain.endswith('.' + skipped):
            return True
    return False
