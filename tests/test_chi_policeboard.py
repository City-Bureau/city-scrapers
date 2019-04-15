from datetime import datetime

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from tests.utils import file_response

from city_scrapers.spiders.chi_policeboard import ChiPoliceBoardSpider

test_response = file_response(
    'files/chi_policeboard_public_meetings.html',
    url='https://www.cityofchicago.org/city/en/depts/cpb/provdrs/public_meetings.html'
)
spider = ChiPoliceBoardSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_title():
    assert parsed_items[0]['title'] == 'Board of Directors'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == ''


def test_start():
    assert parsed_items[8]['start'] == datetime(2017, 9, 18, 19, 30)


def test_links():
    assert parsed_items[8]['links'] == [
        {
            'href':
                'https://www.cityofchicago.org/content/dam/city/depts/cpb/PubMtgMinutes/BlueBook09182017.pdf',  # noqa
            'title': 'Blue Book'
        },
        {
            'href':
                'https://www.cityofchicago.org/content/dam/city/depts/cpb/PubMtgMinutes/PubMtgTranscript09182017.pdf',  # noqa
            'title': 'Transcript'
        },
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end'] is None


def test_id():
    assert parsed_items[8]['id'] == 'chi_policeboard/201709181930/x/board_of_directors'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


def test_status():
    assert parsed_items[8]['status'] == PASSED


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'address': '3510 S Michigan Ave, Chicago IL 60653',
        'name': 'Chicago Public Safety Headquarters',
    }


@pytest.mark.parametrize('item', parsed_items)
def test_source(item):
    assert item['source'
                ] == 'https://www.cityofchicago.org/city/en/depts/cpb/provdrs/public_meetings.html'
