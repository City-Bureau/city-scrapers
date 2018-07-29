from functools import reduce
from functools import wraps
from operator import getitem
from scrapy_sentry.utils import get_client


def get_key(the_dict, location_string):
    """
    Get nested dict key using dot notation.

    ```
    get_key(mydict, 'key1.key2')
    ```
    """

    try:
        return reduce(getitem, location_string.split('.'), the_dict) or ''
    except (KeyError, TypeError):
        return None

def report_error(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            get_client().captureException(extra={
                'args': args,
                'kwargs': kwargs
            })
            raise

    return wrapper
