import re
from datetime import date, time

from city_scrapers.constants import CLASSIFICATIONS, STATUSES


class TravisValidationPipeline(object):
    NULL_VALUES = [None, '']
    SCHEMA = {
        '_type': {'required': True, 'type': str, 'values': ['event']},
        'id': {'required': True, 'type': str, 'format_str': '.+/\d{12}/.+/.+'},
        'name': {'required': True, 'type': str},
        'event_description': {'required': False, 'type': str},
        'all_day': {'required': True, 'type': bool},
        'status': {'required': True, 'type': str, 'values': STATUSES},
        'classification': {
            'required': False,
            'type': str,
            'values': CLASSIFICATIONS,
        },
        'start': {'required': True, 'type': dict},
        'end': {'required': True, 'type': dict},
        'location': {'required': True, 'type': dict},
        'documents': {'required': False, 'type': list},
        'sources': {'required': True, 'type': list}
    }
    START_SCHEMA = {
        'date': {'required': True, 'type': date},
        'time': {'required': False, 'type': time},
        'note': {'required': False, 'type': str}
    }
    END_SCHEMA = {
        'date': {'required': False, 'type': date},
        'time': {'required': False, 'type': time},
        'note': {'required': False, 'type': str}
    }
    LOCATION_SCHEMA = {
        'name': {'required': False, 'type': str},
        'address': {'required': True, 'type': str},
        'neighborhood': {'required': False, 'type': str}
    }
    DOCUMENTS_SCHEMA = {
        'url': {'required': True, 'type': str},
        'note': {'required': True, 'type': str}
    }
    SOURCES_SCHEMA = {
        'url': {'required': True, 'type': str},
        'note': {'required': False, 'type': str}
    }

    def process_item(self, item, spider):
        '''
        Adds validation fields to an item.
        '''
        # Don't validate events in the past
        try:
            start = item['start']['start_date']
            if start < date.today():
                return {}
        except (KeyError, TypeError):
            pass

        # Create a dict with validation fields from self.SCHEMA
        validation_record = self._validate_against_schema(item, self.SCHEMA)

        # unpack start, end and location dictionaries
        start = item.get('start', {})
        if not isinstance(start, dict):
            start = {}
        end = item.get('end', {})
        if not isinstance(end, dict):
            end = {}
        location = item.get('location', {})
        if not isinstance(location, dict):
            location = {}

        # Add validation fields from self.START_SCHEMA and self.END_SCHEMA
        validation_record.update(
            self._validate_against_schema(
                start, self.START_SCHEMA, 'start'
            )
        )
        validation_record.update(
            self._validate_against_schema(
                end, self.END_SCHEMA, 'end'
            )
        )
        validation_record.update(
            self._validate_against_schema(
                location, self.LOCATION_SCHEMA, 'loc'
            )
        )

        # Add validation fields from self.DOCUMENTS_SCHEMA, self.SOURCES_SCHEMA
        validation_record.update(
            self._validate_list(
                item.get('documents', []), self.DOCUMENTS_SCHEMA, 'doc'
            )
        )
        validation_record.update(
            self._validate_list(
                item.get('sources', []), self.SOURCES_SCHEMA, 'sources'
            )
        )

        # Add validation fields to item
        item.update(validation_record)
        return item

    def _validate_list(self, list_of_items, schema, prefix=''):
        """
        Validates a list of items against a schema. Returns a dictionary of
        validation fields with value = 1 if ALL of the items are valid and
        value = 0 if ANY one of the items is invalid.
        """
        if not list_of_items:
            return {}
        list_of_validations = []
        combined_validation = {}

        # Validate each item against the schema to get a
        # list of validation dicts
        for item in list_of_items:
            list_of_validations.append(
                self._validate_against_schema(item, schema, prefix)
            )

        # Combine all the validation dicts into one dictionary that has value
        # = 1 if ALL the items are valid, and 0 if ANY one of the items is
        # invalid
        for key in list_of_validations[0].keys():
            combined_validation[key] = all([
                d[key] for d in list_of_validations
            ])
        return combined_validation

    def _validate_against_schema(self, item, schema, prefix=''):
        """
        Returns a dictionary with key='val_{field}',
        value = 1 if item[field] is valid, and value = 0 if item[field]
        is invalid according to the schema.

        Examples:
        >> schema = {
            'name': {'required': True, 'type': str},  # required field
            'event_description': {'required': False, 'type': str}
            # not required
        }
        >> item1 = {
            'name': 'A Committee Meeting on Pedestrian Safety',  # valid
            'event_description': float(5)                        # invalid
        }
        >> self._validate_against_schema(item1, schema)
        {
            'val_name': 1,
            'val_event_description': 0
        }

        >> item2 = {
            'name': '',                                            # invalid
            'event_description': 'This is a meeting about safety.' # valid
        }
        >> self._validate_against_schema(item2, schema)
        {
            'val_name': 0,
            'val_event_description': 1
        }
        """
        validation_record = {}
        for field in schema:
            new_key = 'val_{0}_{1}'.format(prefix, field).replace('__', '_')
            is_valid = True
            is_required = schema[field]['required']
            if not is_required and (item.get(field, None) in self.NULL_VALUES):
                is_valid = True
            else:
                if is_required:
                    is_valid = not (item.get(field, None) in self.NULL_VALUES)
                if 'type' in schema[field]:
                    correct_type = isinstance(
                        item.get(field, None), schema[field]['type']
                    )
                    is_valid = is_valid and correct_type
                if 'values' in schema[field]:
                    in_values = (
                        item.get(field, None) in schema[field]['values']
                    )
                    is_valid = is_valid and in_values
                if 'format_str' in schema[field]:
                    pattern = re.compile(schema[field]['format_str'])
                    try:
                        match = re.match(pattern, item.get(field, ''))
                    except TypeError:
                        is_valid = False
                    else:
                        if not match:
                            is_valid = False
            validation_record[new_key] = int(is_valid)
        return validation_record
