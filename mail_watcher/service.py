import logging

from mail_watcher.config import MailWatcherSettings
from mail_watcher.inbox import GmailInbox
from mail_watcher.models import IncomingMail
from mail_watcher.policy import is_reply, is_skipped_sender
from mail_watcher.telegram import TelegramNotifier

logger = logging.getLogger(__name__)


class MailWatcherService:
    def __init__(self, settings: MailWatcherSettings) -> None:
        self._settings = settings
        self._inbox = GmailInbox(settings)
        self._telegram = TelegramNotifier(settings)

    def poll_once(self) -> None:
        mails = self._inbox.fetch_unseen()
        if not mails:
            return
        logger.info('Unseen inbox messages: %s', len(mails))
        seen: list[str] = []
        for mail in mails:
            try:
                if self._handle(mail):
                    seen.append(mail.uid)
            except Exception:
                logger.exception('Failed uid=%s from=%s', mail.uid, mail.from_addr)
        self._inbox.mark_seen(seen)

    def _handle(self, mail: IncomingMail) -> bool:
        if is_skipped_sender(mail, self._settings):
            logger.info('Read-only skip sender %s uid=%s', mail.from_addr, mail.uid)
            return True
        if is_reply(mail):
            logger.info('Skip reply uid=%s subject=%s', mail.uid, mail.subject)
            return True
        self._telegram.send_mail(mail)
        logger.info('Processed uid=%s from=%s', mail.uid, mail.from_addr)
        return True
