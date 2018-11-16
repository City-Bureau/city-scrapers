import os
import json
from collections import defaultdict
from functools import reduce


def validate_spider(spider_file):
    """
    Validates scraped items from a spider.
    Passes if >=90% of the scraped items
    conform to the schema.
    """
    spider = os.path.basename(spider_file).split('.')[0]
    # Open a JSON of scraped items
    with open(spider_file, 'r') as f:
        content = f.read()
        if len(content) == 0:
            print("{0} was empty.".format(spider_file))
            return None
        try:
            scraped_items = json.loads(content)
        except json.decoder.JSONDecodeError:
            message = (
                "Could not decode JSON. Here is the beginning and end of the file: {0}\n...\n{1}"
            )
            print(message).format(content[:50], content[-50:])
            raise Exception("Could not decode JSON")

    # Drop empty items
    nonempty_items = [item for item in scraped_items if item]

    # Reformat items from a list of dicts into a dict of lists
    # Keep only the validation keys (that start with 'val_')
    validated_items = defaultdict(list)
    for item in nonempty_items:
        for k, v in item.items():
            if k.startswith('val_'):
                validated_items[k].append(v)

    print('\n------------Validation Summary for: {0}---------------'.format(spider))
    print('Validating {} items\n'.format(len(nonempty_items)))
    validation_summary = {}
    for item_key, item_list in validated_items.items():
        validation_summary[item_key] = reduce(lambda x, y: x + y, item_list) / len(item_list)
        print('{}: {:.0%}'.format(item_key[4:], validation_summary[item_key]))

    try:
        assert all([x >= 0.9 for x in validation_summary.values()])
    except AssertionError as e:
        message = (
            'Less than 90% of the scraped items from {0} passed validation. '
            'See the validation summary printed in stdout, and check that the '
            'scraped items conform to the events schema at: '
            'https://github.com/City-Bureau/city-scrapers/'
            'blob/master/docs/06_event_schema.md'
        ).format(spider)
        raise Exception(message) from e
