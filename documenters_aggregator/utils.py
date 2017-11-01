from functools import reduce
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
