import pytest
from datetime import date, time
from freezegun import freeze_time
from tests.utils import file_response
from city_scrapers.constants import COMMITTEE, CONFIRMED
from city_scrapers.spiders.cook_landbank import CookLandbankSpider

freezer = freeze_time('2018-09-13 12:00:00')
freezer.start()

file = file_response('files/cook_landbank.json')
spider = CookLandbankSpider()

test_response = file
parsed_items = list(spider.parse(test_response))

freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'CCLBA Land Transactions Committee'


def test_event_description():
    assert parsed_items[0]['event_description'] == (
        'The Land Transactions Committee will convene on Friday, September '
        '14th at the hour of 10:00 AM at the location of 69 W. Washington '
        'St., 22nd Floor, Conference Room ‘B”, Chicago, Illinois, to consider '
        'the following:'
    )


def test_start():
    EXPECTED_START = {
        'date': date(2018, 9, 14),
        'time': time(10, 00),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START


def test_end():
    EXPECTED_END = {
        'date': date(2018, 9, 14),
        'time': None,
        'note': ''
    }
    assert parsed_items[0]['end'] == EXPECTED_END


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == COMMITTEE


def test_status():
    assert parsed_items[0]['status'] == CONFIRMED


def test_location():
    assert parsed_items[0]['location'] == {
        'url': 'http://www.cookcountylandbank.org/',
        'name': None,
        'address': '69 W. Washington St., Lower Level Conference Room A',
        'coordinates': {
            'latitude': None, 'longitude': None
        }
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': (
            'http://www.cookcountylandbank.org/events/'
            'cclba-land-transactions-committee-09142018/'
        ),
        'note': 'Event Page'
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [{
        'url': (
            'http://www.cookcountylandbank.org/wp-content/'
            'uploads/2018/09/CCLBA-Land-Transaction-9-14-18-Agenda.pdf'
        ), 'note': 'Agenda'
    }]


def test__type():
    assert parsed_items[0]['_type'] == 'event'
