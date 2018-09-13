import pytest
from datetime import date, time
from tests.utils import file_response
from city_scrapers.constants import COMMITTEE
from city_scrapers.spiders.cook_landbank import CookLandbankSpider

file = file_response('files/cook_landbank.json')
spider = CookLandbankSpider()

test_response = file
parsed_items = list(spider.parse(test_response))


def test_name():
    assert parsed_items[0]['name'] == 'CCLBA Finance Committee Meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_event_description(item):
    assert item['event_description'] == ("The Cook County Land Bank Authority Finance Committee will meet on Wednesday, September 13th, 2017 at the hour of 10:00 AM in the Cook County Administration Building located at 69 W. Washington St., 22nd Floor, Conference Room ‘A’, Chicago, Illinois, to consider the following:")


def test_start():
    EXPECTED_START = {
        'date': date(2017, 9, 13),
        'time': time(10, 00),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START


def test_end():
    EXPECTED_END = {
        'date': None,
        'time': None,
        'note': ''
    }
    assert parsed_items[0]['end'] == EXPECTED_END


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


# def test_id():
#    assert parsed_items[0]['id'] == 'cook_landbank/201709131000/3381/cclba_finance_committee_meeting'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == COMMITTEE


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': 'http://www.cookcountylandbank.org/',
        'name': None,
        'address': "Cook County Administration Building, 69 W. Washington St., 22nd Floor, Conference Room 'A', Chicago, IL 60602",
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.cookcountylandbank.org/events/cclba-finance-committee-meeting-09132017/',
        'note': "Event Page",
    }]

def test_documents():
    assert parsed_items[0]['documents'] == [{
        'url': 'http://www.cookcountylandbank.org/wp-content/uploads/2017/09/CCLBA.Finance.Committee_09.13.2017.pdf',
        'note': 'agenda'
    }]


def test__type():
    assert parsed_items[0]['_type'] == 'event'
