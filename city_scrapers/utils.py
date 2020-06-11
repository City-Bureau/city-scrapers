from functools import wraps

from scrapy_sentry.utils import get_client


def report_error(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            get_client().captureException(extra={"args": args, "kwargs": kwargs})
            raise

    return wrapper
