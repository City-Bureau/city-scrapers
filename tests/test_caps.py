import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.caps import CapsSpider
from datetime import datetime

def test_tests():
    print('Please write some tests for this spider or at least disable this one.')
    assert True


"""
Uncomment below
"""

test_response = file_response('files/caps.json')
spider = CapsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
     assert isinstance(parsed_items[0]['name'], str)


def test_description():
    assert isinstance(parsed_items[0]['description'], str)


def test_end_time():
    assert isinstance(parsed_items[0]['end_time'], datetime)

def test_id():
    assert isinstance(parsed_items[0]['id'], int)


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'CAPS community event'


def test_status():
    assert parsed_items[0]['status'] == 'confirmed'


def test_location():
    assert isinstance(parsed_items[0]['location']['name'], str)


def test__type():
    assert isinstance(parsed_items[0]['_type'], str)
