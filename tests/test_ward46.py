from tests.utils import file_response
from documenters_aggregator.spiders.ward46 import Ward46Spider
import datetime

test_response = file_response('files/ward46.html')
spider = Ward46Spider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == '46th Ward Office Closed for Labor Day'


def test_start_time():
    assert type(parsed_items[0]['start_time']) == datetime.datetime


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == 'post-1851'


def test_all_day():
    assert parsed_items[0]['all_day'] is True


def test_classification():
    assert parsed_items[0]['classification'] == 'Not classified'


def test_status():
    assert parsed_items[0]['status'] == 'tentative'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': None,
        'name': '',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test__type():
    assert parsed_items[0]['_type'] == 'event'
