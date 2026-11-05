from mail_watcher.config import MailWatcherSettings
from mail_watcher.models import IncomingMail


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
