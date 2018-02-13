import json
from tests.utils import read_test_file_content
from documenters_aggregator.pipelines.TravisValidation import TravisValidationPipeline


fixtures = json.loads(read_test_file_content('files/travis_fixture.json'))
pipeline = TravisValidationPipeline()


def test_process_item():
    processed = pipeline.process_item(fixtures[0], None)
    for k, v in pipeline.SCHEMA.items():
        if v['required']:
            assert processed['val_{}'.format(k)] == 1
        else:
            assert processed['val_{}'.format(k)] in [0, 1]


def test_validate_location():
    item = fixtures[0]
    item['location']['name'] = None
    processed = pipeline.process_item(item, None)
    assert processed['val_loc_name'] == 0


def test_validate_coordinates():
    # Should be float, not string
    item = fixtures[0]
    item['location']['coordinates']['latitude'] = 10.0
    processed = pipeline.process_item(item, None)
    assert processed['val_coord_latitude'] == 0


def test_validate_sources():
    item = fixtures[0]
    item['sources'].append({})
    processed = pipeline.process_item(item, None)
    assert processed['val_sources'] == 0
