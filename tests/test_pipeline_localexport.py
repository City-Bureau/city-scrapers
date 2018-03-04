import json
from tests.utils import read_test_file_content
from documenters_aggregator.pipelines.localExporter import CsvPipeline


fixtures = json.loads(read_test_file_content('files/travis_fixture.json'))
valid_item = fixtures[0]
pipeline = CsvPipeline()


def test_valid_process_item():
    processed = pipeline.process_item(valid_item, None)
    for k, v in processed.items():
        if k.startswith('val_'):
            assert v == 1


def test_invalid_required_value():
    invalid_item = valid_item.copy()
    invalid_item['id'] = ''
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_id'] == 0


def test_invalid_type():
    invalid_item = valid_item.copy()
    invalid_item['id'] = True
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_id'] == 0


def test_invalid_format():
    invalid_item = valid_item.copy()
    invalid_item['id'] = 'invalid-id-format'
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_id'] == 0


def test_invalid_location():
    invalid_item = valid_item.copy()
    invalid_item['location']['address'] = ''
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_loc_address'] == 0


def test_invalid_coordinates():
    # Should be string, not a float
    invalid_item = valid_item.copy()
    invalid_item['location']['coordinates']['latitude'] = 10.0
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_coord_latitude'] == 0


def test_invalid_sources():
    invalid_item = valid_item.copy()
    invalid_item['sources'].append({})
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_sources'] == 0
