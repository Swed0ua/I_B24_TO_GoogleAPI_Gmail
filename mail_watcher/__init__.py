"""Mail watcher package. Lazy export — не тягне runner/config при import process."""

__all__ = ['start_mail_watcher']


def __getattr__(name: str):
    if name == 'start_mail_watcher':
        from mail_watcher.runner import start_mail_watcher

        return start_mail_watcher
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
