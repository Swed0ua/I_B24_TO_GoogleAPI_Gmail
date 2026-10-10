import logging
import time

from mail_watcher.config import load_settings
from mail_watcher.service import MailWatcherService

logger = logging.getLogger(__name__)


def run_mail_watcher() -> None:
    """Blocking poll loop — окремий процес/сервіс."""
    settings = load_settings()
    if not settings.enabled:
        logger.info('Mail watcher disabled (MAIL_WATCHER_ENABLED=false)')
        return
    if not settings.ready:
        logger.error(
            'Mail watcher secrets missing: %s and %s',
            settings.client_secret_path,
            settings.token_path,
        )
        return

    service = MailWatcherService(settings)
    logger.info('Mail watcher running every %ss', settings.poll_interval_sec)
    while True:
        try:
            service.poll_once()
        except Exception:
            logger.exception('Mail watcher poll failed')
        time.sleep(settings.poll_interval_sec)


def start_mail_watcher() -> None:
    """Alias for entrypoint compatibility."""
    run_mail_watcher()
