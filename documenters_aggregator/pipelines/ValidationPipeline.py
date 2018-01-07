import re


class ValidationPipeline(object):
    NULL_VALUES = [None, '']
    SCHEMA = {
        '_type': {'required': True, 'type': str, 'values': ['event']},
        'id': {'required': True, 'type': str, 'format_str': '.+/\d{12}/.+/.+'},
        'name': {'required': True, 'type': str},
        'description': {'required': False, 'type': str},
        'classification': {'required': True, 'type': str},
        'start_time': {'required': True, 'type': str, 'format_str': '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-0(5|6):00'},
        'end_time': {'required': False, 'type': str, 'format_str': '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-0(5|6):00'},
        'timezone': {'required': True, 'type': str},
        'all_day': {'required': True, 'type': bool},
        'location': {'required': True, 'type': dict},
        'sources': {'required': True, 'type': list}
    }
    LOCATION_SCHEMA = {
        'url': {'required': False, 'type': str},
        'name': {'required': False, 'type': str},
        'address': {'required': True, 'type': str},
        'coordinates': {'required': True, 'type': dict}
    }
    COORDINATES_SCHEMA = {
        'latitude': {'required': True, 'type': str},
        'longitude': {'required': True, 'type': str}
    }
    SOURCES_SCHEMA = {
        'url': {'required': True, 'type': str},
        'note': {'required': False, 'type': str}
    }

    def process_item(self, item, spider):
        '''
        Adds validation fields to an item.
        '''
        item_location = item.get('location', {})
        if not isinstance(item_location, dict):
            item_location = {}
        item_coordinates = item.get('location', {'coordinates': {}}).get('coordinates', {})
        if not isinstance(item_coordinates, dict):
            item_coordinates = {}

        validation_record = self._validate_against_schema(item, self.SCHEMA)
        validation_record.update(self._validate_against_schema(item_location, self.LOCATION_SCHEMA, 'loc'))
        validation_record.update(self._validate_against_schema(item_coordinates, self.COORDINATES_SCHEMA, 'coord'))

        is_sources_valid = validation_record['val_sources']
        for source in item.get('sources', []):
            source_validation = self._validate_against_schema(source, self.SOURCES_SCHEMA)
            is_sources_valid = is_sources_valid and all(source_validation.values())
        validation_record.update({'val_sources': str(is_sources_valid)})

        item.update(validation_record)
        return item

    def _validate_against_schema(self, item, schema, prefix=''):
        """
        For each field in schema, create a dictionary entry
        (key='val_{field}': value=True/False) where the value
        indicates whether or not item[field] conforms to the schema.
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
                    correct_type = isinstance(item.get(field, None), schema[field]['type'])
                    is_valid = is_valid and correct_type
                if 'values' in schema[field]:
                    in_values = (item.get(field, None) in schema[field]['values'])
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
            validation_record[new_key] = str(is_valid)  # airtable ignores boolean False's
        return validation_record
