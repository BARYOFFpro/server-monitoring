import functools
import pprint

from logger_config import setup_logger

_log = setup_logger()


class DebugHelper:
    """Отладочный класс: log(), dump(), trace()."""

    def __init__(self, enabled=True):
        self.enabled = enabled

    def log(self, message):
        if self.enabled:
            print(f"[DEBUG] {message}")
            _log.debug(message)

    def dump(self, obj, name="object"):
        if self.enabled:
            print(f"[DUMP] {name} ({type(obj).__name__}):")
            pprint.pprint(vars(obj) if hasattr(obj, "__dict__") else obj)

    def trace(self, func):
        """Декоратор: печатает вызов функции, аргументы и результат."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.enabled:
                print(f"[TRACE] вызов {func.__name__}{args}")
            result = func(*args, **kwargs)
            if self.enabled:
                print(f"[TRACE] {func.__name__} вернула {result}")
            return result
        return wrapper
