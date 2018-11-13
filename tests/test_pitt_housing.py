import pytest
from datetime import date, time

from tests.utils import file_response
from city_scrapers.constants import *
from city_scrapers.spiders.pitt_housing import PittHousingSpider


# def test_tests():
#     print('Please write some tests for this spider or at least disable this one.')
#     assert False

"""
Uncomment below
"""

test_response = file_response('files/pitt_housing_board-info.html')
spider = PittHousingSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Housing Authority of the City of Pittsburgh'


def test_description():
    assert parsed_items[0]['event_description'] == 'Board of Commissioners meeting'


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2018, 1, 25), 'time': None, 'note': None}

def test_end():
    assert parsed_items[0]['end'] == {'date': None, 'time': None, 'note': None}


def test_id():
    assert parsed_items[0]['id'] == 'pitt_housing/201801250000/x/housing_authority_of_the_city_of_pittsburgh'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {'address': '',
                    'name': '',
                    'neighborhood': ''
                }

def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.hacp.org/public-information/board-info',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [{
      'url': 'http://static1.firemandev.info.s3.amazonaws.com/galleries/general/2018%20Board%20Information/Board_Agenda_-_JANUARY_2018.pdf',
      'note': 'agenda'
    },
    {
      'url': 'http://static1.firemandev.info.s3.amazonaws.com/galleries/general/2018%20Board%20Information/Board_Minutes_-_January_2018.pdf',
      'note': 'minutes'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
