## Framework copied from test_ward_night to update

import pytest
from datetime import date, time, datetime
from pytz import timezone

from tests.utils import file_response
from city_scrapers.constants import COMMITTEE
from city_scrapers.spiders.chi_localschoolcouncil import ChiLocalSchoolCouncilSpider
from textwrap import dedent

test_response = file_response('files/tests_chilocal_events.json')
spider = ChiLocalSchoolCouncilSpider(start_date=datetime(2018, 1, 1))
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_id():
    assert parsed_items[0]['id'] == 'chi_localschoolcouncil/201801081600/x/local_school_council_fort_dearborn_es'


def test_name():
    assert parsed_items[0]['name'] == 'Local School Council: Fort Dearborn ES'


def test_start():
    EXPECTED_START = {
        'date': date(2018, 1, 8),
        'time': time(16, 0),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START


def test_end():
    EXPECTED_END = {
        'date': date(2018, 1, 8),
        'time': time(19, 0),
        'note': 'estimated 3 hours after start time'
    }
    assert parsed_items[0]['end'] == EXPECTED_END


def test_location():
    assert parsed_items[0]['location'] == {
        'name': '',
        'address': '9025 S Throop St 60620',
        'neighborhood': 'Washington Heights'
    }


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_documents():
    assert parsed_items[0]['documents'] == []


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://docs.google.com/spreadsheets/d/1uzgWLWl19OUK6RhkAuqy6O6p4coTOqA22_nmKfzbakE',
        'note': 'Google Sheet that Darryl filled out manually'
    }]


def test_classification():
    assert parsed_items[0]['classification'] is COMMITTEE


def test__type():
    assert parsed_items[0]['_type'] == 'event'

