import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.caps import CapsSpider

def test_tests():
    print('Please write some tests for this spider or at least disable this one.')
    assert True


"""
Uncomment below
"""

test_response = file_response('../documenters_aggregator/spiders/caps.py')
spider = CapsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'National Night Out -- Beat 2433'


def test_description():
    assert parsed_items[0]['description'] == 'Join friends, neighbors and police to stand up against crime in your neighborhood'


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-08-01T18:00:00'


def test_end_time():
    assert parsed_items[0]['end_time'] == '2017-08-01T20:00:00'


def test_id():
    assert parsed_items[0]['id'] == '24'


def test_all_day(item):
    assert parsed_items[0]['all_day'] is False


def test_classification(item):
    assert parsed_items[0]['classification'] == None


def test_status(item):
    assert parsed_items[0]['status'] == 'confirmed'


def test_location(item):
    assert item['location'] == {
        'url': None,
        'name': 'Swift School at Thorndale and Winthrop',
        'coordinates': {
            'latitude': 'EXPECTED LATITUDE',
            'longitude': 'EXPECTED LONGITUDE',
        },
    }


def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
