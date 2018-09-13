import json
from datetime import datetime, date, time
from tests.utils import read_test_file_content
from city_scrapers.pipelines import TravisValidationPipeline
from city_scrapers.spider import Spider


def _str_to_date(date_string):
    try: 
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except:
        return None 

def _str_to_time(time_string):
    try: 
        return datetime.strptime(date_string, "%Y-%m-%d").time()
    except:
        return None


def load_valid_item():
    fixtures = json.loads(read_test_file_content('files/travis_fixture.json'))
    valid_item = fixtures[0]
    valid_item['start']['date'] = _str_to_date(valid_item['start']['date'])
    valid_item['start']['time'] = _str_to_time(valid_item['start']['time'])
    return valid_item


valid_item = load_valid_item()
pipeline = TravisValidationPipeline()


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


def test_invalid_start_date():
    invalid_item = valid_item.copy()
    invalid_item['start']['date'] = None
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_start_date'] == 0


def test_invalid_start_time():
    invalid_item = valid_item.copy()
    invalid_item['start']['time'] = True
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_start_time'] == 0


def test_invalid_location():
    invalid_item = valid_item.copy()
    invalid_item['location']['address'] = ''
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_loc_address'] == 0


def test_invalid_documents():
    invalid_item = valid_item.copy()
    invalid_item['documents'].append({'url': 'www.example.com', 'note': ''})
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_doc_note'] == 0


def test_invalid_sources():
    invalid_item = valid_item.copy()
    invalid_item['sources'].append({'url': '', 'note': 'agenda'})
    processed = pipeline.process_item(invalid_item, None)
    assert processed['val_sources_url'] == 0
