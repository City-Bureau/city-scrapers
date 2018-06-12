import pytest
import json

from city_scrapers.spiders.chi_water import Chi_waterSpider

test_response = []
with open('tests/files/chi_water_test.json') as f:
    test_response.extend(json.loads(f.read()))
spider = Chi_waterSpider()
# This line throws error
parsed_items = [item for item in spider._parse_events(test_response)]

##### Test Single Instance #####

def test_name():
    assert parsed_items[0]['name'] == 'Board of Commissioners'

def test_description():
    assert parsed_items[0]['description'] == 'no agenda posted'

def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2018-12-20T10:30:00-06:00'

# def test_id():
#    assert parsed_items[0]['id'] == 'chi_water/201812201030/x/board_of_commissioners'

def test_location():
    assert parsed_items[0]['location'] == {
    'address': 'Board Room',
    'coordinates': {'latitude': None, 'longitude': None},
    'name': None,
    'url': None}

def test_sources():
    assert parsed_items[0]['sources'] == [{'note': '',
   'url': 'https://mwrd.legistar.com/DepartmentDetail.aspx?ID=1622&GUID=5E16B4CD-0692-4016-959D-3F080D6CFFB4'}]


##### Parameterized Tests #####

@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] is 'event'

@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False

@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'

@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end_time'] is None

@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] is 'tentative'

@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['timezone'] == 'America/Chicago'


