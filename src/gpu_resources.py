"""Cooperative cross-worktree GPU lease; never remove another task's lock automatically."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import threading

_MUTEX = threading.RLock()
_LOCAL = threading.local()


@contextmanager
def gpu_lease(task: str):
    with _MUTEX:
        if getattr(_LOCAL, 'active', False):
            yield
            return
        path=Path(os.environ.get('MOTION_GPU_LOCK',str(Path.home()/'MotionLibrary/gpu.lock')))
        path.parent.mkdir(parents=True,exist_ok=True)
        try:
            handle=path.open('x',encoding='utf-8')
        except FileExistsError as exc:
            raise RuntimeError(f'GPU reserved: {path}. Wait for its owner; verify host/PID before manual recovery.') from exc
        with handle:
            handle.write(json.dumps(dict(pid=os.getpid(),host=socket.gethostname(),task=task)))
        _LOCAL.active=True
        try:
            yield
        finally:
            _LOCAL.active=False
            path.unlink(missing_ok=True)


def gpu_task(name):
    from functools import wraps
    def decorate(function):
        @wraps(function)
        def run(*args, **kwargs):
            with gpu_lease(name):
                return function(*args, **kwargs)
        return run
    return decorate
