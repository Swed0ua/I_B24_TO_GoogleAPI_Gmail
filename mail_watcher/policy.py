import re

from mail_watcher.config import MailWatcherSettings
from mail_watcher.models import IncomingMail

# Outlook / Gmail quoted thread markers — keep only text above them.
_QUOTE_SPLIT = re.compile(
    r'(?m)^(?:'
    r'-{2,}\s*Original Message\s*-{2,}'
    r'|_{5,}'
    r'|From:\s+.+\s*$'
    r'|On .+ wrote:\s*$'
    r'|Від:\s+.+\s*$'
    r')',
    re.IGNORECASE,
)
_CID_NOISE = re.compile(r'\[cid:[^\]]+\](?:<[^>]*>)?', re.IGNORECASE)
_MULTI_BLANK = re.compile(r'\n{3,}')


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


def latest_body(text: str) -> str:
    """Return only the newest message, without quoted reply history."""
    if not text:
        return ''
    match = _QUOTE_SPLIT.search(text)
    head = text[: match.start()] if match else text
    head = _CID_NOISE.sub('', head)
    head = _MULTI_BLANK.sub('\n\n', head)
    return head.strip()
