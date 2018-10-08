from datetime import date, time
import pytest
from tests.utils import file_response
from city_scrapers.constants import POLICE_BEAT
from city_scrapers.spiders.chi_police import ChiPoliceSpider

test_response = file_response('files/chi_police.json')
spider = ChiPoliceSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'CAPS District 25, Beat 14'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    EXPECTED_START = {
        'date': date(2017, 12, 28),
        'time': time(18, 30),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START


def test_end_time():
    EXPECTED_END = {
        'date': date(2017, 12, 28),
        'time': time(19, 30),
        'note': ''
    }
    assert parsed_items[0]['end'] == EXPECTED_END


def test_id():
    assert parsed_items[0]['id'] == 'chi_police/201712281830/25/caps_district_25_beat_14'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_classification():
    assert parsed_items[0]['classification'] == POLICE_BEAT


def test_documents():
    assert parsed_items[0]['documents'] == []


def test_location():
    EXPECTED_LOCATION = {
            'address': "St. Ferdinand's3115 N. Mason Chicago, IL",
            'name': '',
            'neighborhood': ''
    }
    assert parsed_items[0]['location'] == EXPECTED_LOCATION


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_sources():
    EXPECTED_SOURCES = [{'url': 'https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars',
                         'note': ''}]
    assert parsed_items[0]['sources'] == EXPECTED_SOURCES
