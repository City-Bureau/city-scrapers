from datetime import date, time

import pytest

from city_scrapers.constants import BOARD
from city_scrapers.spiders.chi_boardofethics import ChiBoardOfEthicsSpider
from tests.utils import file_response

test_response = file_response('files/chi_boardofethics.html')
spider = ChiBoardOfEthicsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
parsed_meeting_text = 'All meetings will be held at 12:00 PM and typically last about 2 hours\xa0 Meetings are held ' \
                      'at the City of Chicago Board of Ethics, 740 N. Sedgwick, Ste. 500, Chicago, IL 60654-8488.'


def test_items():
    assert len(parsed_items) == 7


def test_name():
    assert parsed_items[0]['name'] == 'Board of Directors'


def test_description():
    assert parsed_items[0]['event_description'] == parsed_meeting_text


def test_start_time():
    assert parsed_items[0]['start']['date'] == date(2018, 6, 15)
    assert parsed_items[0]['start']['time'] == time(12, 00)
    assert parsed_items[0]['start']['note'] == ''


def test_end_time():
    assert parsed_items[0]['end']['date'] == date(2018, 6, 15)
    assert parsed_items[0]['end']['time'] == time(14, 00)
    assert parsed_items[0]['end']['note'] == ''


def test_id():
    assert parsed_items[0]['id'] == 'chi_boardofethics/201806151200/x/board_of_directors'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': '',
        'name': 'City of Chicago Board of Ethics',
        'address': '740 N. Sedgwick, Ste. 500, Chicago, IL 60654-8488',
        'neighborhood': '',
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.cityofchicago.org/city/en/depts/ethics/supp_info/minutes.html',
        'note': ''
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
