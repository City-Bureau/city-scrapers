import json
import re

NULL_VALUES = [None, '']

SCHEMA = {
    '_type': {'required': True, 'values': ['event']},
    'id': {'required': True},
    'name': {'required': True, 'type': str},
    'description': {'required': False, 'type': str},
    'classification': {'required': True, 'values': ['committee-meeting', 'hearing']},
    'start_time': {'required': True, 'format_str': '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'},
    'end_time': {'required': False, 'format_str': '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'},
    'timezone': {'required': True, 'values': ['America/Chicago']},
    'all_day': {'required': True, 'type': bool},
    'status': {'required': True, 'values': ['cancelled', 'tentative', 'confirmed', 'passed']},
    'location': {'required': True, 'type': dict}
}

LOCATION_SCHEMA = {
    'url': {'required': False},
    'name': {'required': True, 'type': str},
    'latitude': {'required': True, 'type': str},
    'longitude': {'required': True, 'type': str}
}


class ValidationPipeline(object):
    def __init__(self, schema=SCHEMA, logfile=''):
        '''
        Give a path for logfile if you want to log the
        items that don't conform to the schema.
        '''
        self.logfile = logfile
        self.schema = schema
        self.required_fields = [x for x in self.schema if self.schema[x]['required']]
        self.requires_values = [x for x in self.schema if 'values' in self.schema[x]]
        self.required_types = [x for x in self.schema if 'type' in self.schema[x]]
        self.format_str = [x for x in self.schema if 'format_str' in self.schema[x]]

    def validate_batch(self, batch):
        '''
        Validates a batch of items (e.g., all the items from one spider)
        against the events schema.

        To validate the locations, initialize a ValidationPipeline with
        schema=LOCATION_SCHEMA, extract the location dictionaries from
        the items, and run validate_batch on the location dicts.
        '''
        missing_ids = [item for item in batch if 'id' not in item]
        if missing_ids:
            print("Can't log. Some items are missing id's.")
            self.logfile = ''
        else:
            with open(self.logfile, 'w') as f:
                f.write('LOGGING BAD ITEMS...')

        self.check_required_fields(batch)
        self.check_required_values(batch)
        self.check_required_types(batch)
        self.check_format_str(batch)

    def check_required_fields(self, batch):
        '''
        Checks that a batch of items has the required fields
        '''
        for field in self.required_fields:
            bad_items = [item for item in batch if item.get(field, None) in NULL_VALUES]
            if bad_items:
                message = "{} items are missing {}.\n".format(len(bad_items), field)
                print(message)
                if self.logfile:
                    self._log_bad_items(field, bad_items, message, self.logfile)

    def check_required_values(self, batch):
        '''
        Checks that a batch of items has the required values
        '''
        for field in self.requires_values:
            valid_values = self.schema[field]['values']
            bad_items = [item for item in batch if item.get(field, None) not in valid_values]
            if bad_items:
                message = "{0} items contain invalid values for {1}. Valid values for {1} are: {2}\n".format(len(bad_items), field, str(valid_values))
                print(message)
                if self.logfile:
                    self._log_bad_items(field, bad_items, message, self.logfile)

    def check_required_types(self, batch):
        '''
        Checks that a batch of items has the required types
        '''
        for field in self.required_types:
            valid_type = self.schema[field]['type']
            if field in self.required_fields:
                bad_items = [item for item in batch if type(item.get(field, None)) != valid_type]
            else:
                bad_items = [item for item in batch if (field in item) and (type(item.get(field, None)) != valid_type)]
            if bad_items:
                message = "{0} items contain invalid types for {1}. Valid types for {1} are: {2}\n".format(len(bad_items), field, str(valid_type))
                print(message)
                if self.logfile:
                    self._log_bad_items(field, bad_items, message, self.logfile)

    def check_format_str(self, batch):
        '''
        Checks that a batch of items has strings formatted
        according to the schema
        '''
        for field in self.format_str:
            pattern = re.compile(self.schema[field]['format_str'])
            if field in self.required_fields:
                bad_items = [item for item in batch if not re.match(pattern, item.get(field, None))]
            else:
                bad_items = [item for item in batch if (field in item) and (not re.match(pattern, item.get(field, None)))]
            if bad_items:
                message = "{0} items contain invalid string formatting for {1}. Valid formats for {1} are: {2}\n".format(len(bad_items), field, str(pattern))
                print(message)
                if self.logfile:
                    self._log_bad_items(field, bad_items, message, self.logfile)

    def _log_bad_items(self, field, bad_items, message, logfile):
        '''
        Write bad_items (id: field) to logfile
        '''
        bad_dict = {item['id']: item.get(field, 'ValidationPipeline: FIELD NOT FOUND') for item in bad_items}
        with open(logfile, 'a') as f:
            f.write('\n====================\n')
            f.write(message)
            json.dump(bad_dict, f)
            f.write('\n====================\n')


if __name__ == "__main__":
    # Read in output from scrapy crawl cchhs
    with open('tests/files/cchhs.json', 'r') as f:
        batch = json.loads(f.read())

    # Validate items against events schema
    vp = ValidationPipeline(logfile='tests/files/log_cchhs.txt')
    vp.validate_batch(batch)  # creates log_cchhs.txt

    # Validate items against schema for location dictionary
    location_batch = [item.get('location', {}) for item in batch]
    for idx, item in enumerate(location_batch):
        item.update({'id': batch[idx].get('id', None)})
    vp_location = ValidationPipeline(schema=LOCATION_SCHEMA, logfile='tests/files/log_cchhs_location.txt')
    vp_location.validate_batch(location_batch)  # creates log_cchhs_location.txt
