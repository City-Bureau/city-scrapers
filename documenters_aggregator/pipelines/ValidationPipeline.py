import sys
import json
import re
import logging
import copy

NULL_VALUES = [None, '']
FIELD_NOT_FOUND = 'ValidationPipeline: field not found'
SCHEMA = {
    '_type': {'required': True, 'values': ['event']},
    'id': {'required': True},
    'name': {'required': True, 'type': str},
    'description': {'required': False, 'type': str},
    'classification': {'required': True},
    'start_time': {'required': True, 'format_str': '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-0(5|6):00'},
    'end_time': {'required': False, 'format_str': '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-0(5|6):00'},
    'all_day': {'required': True, 'type': bool},
    'status': {'required': True, 'values': ['cancelled', 'tentative', 'confirmed', 'passed']},
    'location': {'required': True, 'type': dict},
    'sources': {'required': True, 'type': list}
}
LOCATION_SCHEMA = {
    'url': {'required': False},
    'name': {'required': True, 'type': str},
    'latitude': {'required': False, 'type': str},  # actually required
    'longitude': {'required': False, 'type': str}  # actually required
}
SOURCES_SCHEMA = {
    'url': {'required': True, 'type': str},
    'note': {'required': False, 'type': str}
}
VALIDATION_LOGFILE = '../../logs/validation.log'
logging.basicConfig(filename=VALIDATION_LOGFILE, level=logging.DEBUG)


class ValidationPipeline(object):
    def __init__(self, schema=SCHEMA):
        '''
        Initialize a ValidationPipeline object.
        The noncompliance attributes keep track of which
        items are noncompliant for which fields.
        '''
        self.schema = schema
        self.required_fields_noncompliance = {field: {} for field in self.schema if self.schema[field]['required']}
        self.required_values_noncompliance = {field: {} for field in self.schema if 'values' in self.schema[field]}
        self.required_types_noncompliance = {field: {} for field in self.schema if 'type' in self.schema[field]}
        self.format_str_noncompliance = {field: {} for field in self.schema if 'format_str' in self.schema[field]}

    def validate_batch(self, batch):
        '''
        Validates a batch of items (e.g., all the items from one spider)
        against the events schema. Keep track of the noncompliant items
        in ValidationPipeline.required_fields_noncompliance,
        ValidationPipeline.required_values_noncompliance, etc.

        To validate the locations, initialize a ValidationPipeline with
        schema=LOCATION_SCHEMA, extract the location dictionaries from
        the items, and run validate_batch on the location dicts.
        '''
        logger = logging.getLogger(__name__)
        if not batch:
            return

        missing_ids = [item for item in batch if 'id' not in item]
        if missing_ids:
            logger.error("Can't validate. Some items are missing id's.")
            raise KeyError("Can't validate. Some items are missing id's.")

        for item in batch:
            self.check_required_fields(item)
            self.check_required_values(item)
            self.check_required_types(item)
            self.check_format_str(item)

        noncompliance_list = [
            (self.required_fields_noncompliance, '{} items are missing {}.'),
            (self.required_values_noncompliance, '{} items have the wrong values for {}.'),
            (self.required_types_noncompliance, '{} items have the wrong types for {}.'),
            (self.format_str_noncompliance, '{} items have the wrong string formatting for {}.')
        ]

        for noncompliance, message in noncompliance_list:
            self._log_noncompliance(noncompliance, message)

    def _log_noncompliance(self, noncompliance, message):
        '''
        Writes noncompliant items to logs. Formats the
        logs by grouping similarly-noncompliant items
        together to make fixing the spiders easier.
        '''
        logger = logging.getLogger(__name__)
        for field in noncompliance:
            num_items = len(noncompliance[field])
            if num_items > 0:
                logger.warning(message.format(str(num_items), field))
                logger.info('Noncompliant items: {}'.format(str(noncompliance[field])))

    def check_required_fields(self, item):
        '''
        If an item does not have a required field,
        add the item id to the set of noncompliant item ids
        in the ValidationPipeline.
        '''
        for field in self.required_fields_noncompliance:
            if item.get(field, None) in NULL_VALUES:
                noncompliant_item = {item['id']: item.get(field, FIELD_NOT_FOUND)}
                self.required_fields_noncompliance[field].update(noncompliant_item)

    def check_required_values(self, item):
        '''
        If an item does not have a required value,
        add the item to the dict of noncompliant items.
        '''
        for field in self.required_values_noncompliance:
            valid_values = self.schema[field]['values']
            if item.get(field, None) not in valid_values:
                noncompliant_item = {item['id']: item.get(field, FIELD_NOT_FOUND)}
                self.required_values_noncompliance[field].update(noncompliant_item)

    def check_required_types(self, item):
        '''
        If an item does not have a required type,
        add the item to the dict of noncompliant items.

        If the field is required, all items with the wrong type are noncompliant.
        If the field is not required, items with missing values
        are still compliant.
        '''
        for field in self.required_types_noncompliance:
            valid_type = self.schema[field]['type']
            if type(item.get(field, None)) != valid_type:
                if field in self.required_fields_noncompliance:
                    noncompliant_item = {item['id']: item.get(field, FIELD_NOT_FOUND)}
                    self.required_types_noncompliance[field].update(noncompliant_item)
                elif not item.get(field, None) in NULL_VALUES:
                    noncompliant_item = {item['id']: item.get(field, FIELD_NOT_FOUND)}
                    self.required_types_noncompliance[field].update(noncompliant_item)

    def check_format_str(self, item):
        '''
        If a string item is not formatted correctly as a string,
        add the item to the dict of noncompliant items.

        If the field is required, all items with the wrong format are noncompliant.
        If the field is not required, items with missing values
        are still compliant.
        '''
        for field in self.format_str_noncompliance:
            pattern = re.compile(self.schema[field]['format_str'])
            test_string = item.get(field, '')
            if test_string:
                match = re.match(pattern, item.get(field, ''))
                if not match:
                    noncompliant_item = {item['id']: item.get(field, FIELD_NOT_FOUND)}
                    self.format_str_noncompliance[field].update(noncompliant_item)
            elif field in self.required_fields_noncompliance:
                noncompliant_item = {item['id']: item.get(field, FIELD_NOT_FOUND)}
                self.format_str_noncompliance[field].update(noncompliant_item)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # Read in output from scrapy crawl SPIDER_NAME
    SPIDER_NAME = sys.argv[1]
    with open('{0}.json'.format(SPIDER_NAME), 'r') as f:
        batch = json.loads(f.read())

    # Validate items against events schema
    logger.info("VALIDATING AGAINST ==EVENTS== SCHEMA")
    vp = ValidationPipeline()
    vp.validate_batch(batch)

    # Validate items against schema for location dictionary
    location_batch = []
    for item in batch:
        location_item = copy.deepcopy(item['location'])
        location_item.update({'id': item.get('id', None)})
        location_batch.append(location_item)
    logger.info("VALIDATING AGAINST ==LOCATION== SCHEMA")
    vp_location = ValidationPipeline(schema=LOCATION_SCHEMA)
    vp_location.validate_batch(location_batch)

    # Validate items against schema for sources dictionary
    sources_batch = []
    for item in batch:
        for source in item.get('sources', [{}]):
            source_item = copy.deepcopy(source)
            source_item.update({'id': item.get('id', None)})
            sources_batch.append(source_item)
    logger.info("VALIDATING AGAINST ==SOURCES== SCHEMA")
    vp_sources = ValidationPipeline(schema=SOURCES_SCHEMA)
    vp_sources.validate_batch(sources_batch)
