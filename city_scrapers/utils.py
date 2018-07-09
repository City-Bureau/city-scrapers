from functools import reduce
from functools import wraps
from operator import getitem


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
    def wrapper(*args, **kwds):
        try:
            print('Calling decorated function')
            return f(*args, **kwds)
        except:
            # TODO: Report to Sentry
            print('Reporting to Sentry')
            raise

    return wrapper
    