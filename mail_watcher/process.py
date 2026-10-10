"""Запуск mail_watcher окремим OS-процесом (ізольовано від bank pipeline)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _ROOT / 'run_mail_watcher.py'
_child: Optional[subprocess.Popen] = None


def spawn_mail_watcher_process() -> Optional[subprocess.Popen]:
    global _child

    if os.getenv('MAIL_WATCHER_ENABLED', 'true').lower() != 'true':
        print('mail watcher: skipped (MAIL_WATCHER_ENABLED=false)')
        return None

    if not _SCRIPT.is_file():
        print(f'mail watcher: script not found: {_SCRIPT}')
        return None

    if _child is not None and _child.poll() is None:
        return _child

    _child = subprocess.Popen(
        [sys.executable, '-u', str(_SCRIPT)],
        cwd=str(_ROOT),
    )
    print(f'mail watcher: started pid={_child.pid}')
    return _child
