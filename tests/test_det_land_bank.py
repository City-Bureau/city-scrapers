from datetime import datetime

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from tests.utils import file_response

from city_scrapers.spiders.det_land_bank import DetLandBankSpider

test_response = file_response(
    'files/det_land_bank.html', 'https://buildingdetroit.org/events/meetings'
)
spider = DetLandBankSpider()
parsed_items = [item for item in spider.parse(test_response)]
parsed_items = sorted(parsed_items, key=lambda x: x['start'])


def test_title():
    assert parsed_items[0]['title'] == 'Board Of Director Meeting'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2014, 1, 21, 14)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'] == 'det_land_bank/201401211400/x/board_of_director_meeting'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': '',
        'address': '500 Griswold Street, Suite 1200 Detroit, MI 48226'
    }


def test_source():
    assert parsed_items[0]['source'] == 'https://buildingdetroit.org/events/meetings'


def test_links():
    assert parsed_items[0]['links'] == [{
        'href':
            'https://s3.us-east-2.amazonaws.com/dlba-production-bucket/Meetings/documents/01172018085612.pdf',  # noqa
        'title': 'Minutes'
    }]


def test_classification():
    assert parsed_items[0]['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False
