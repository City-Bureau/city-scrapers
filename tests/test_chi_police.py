from datetime import date, time
import pytest
from tests.utils import file_response
from city_scrapers.spiders.chi_police import Chi_policeSpider

test_response = file_response('files/chi_police.json')
spider = Chi_policeSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Beat Meeting, District 25'


def test_description():
    EXPECTED_DESCRIPTION = (
        "CPD Beat meetings, held on all 279 police "
        "beats in the City, provide a regular opportunity "
        "for police officers, residents, and other community "
        "stakeholders to exchange information, identify and "
        "prioritize problems, and begin developing solutions "
        "to those problems."
    )
    assert parsed_items[0]['event_description'] == EXPECTED_DESCRIPTION


def test_start():
    EXPECTED_START = {
        'start_date': date(2017, 12, 28),
        'start_time': time(18, 30),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START


def test_end_time():
    EXPECTED_END = {
        'end_date': date(2017, 12, 28),
        'end_time': time(19, 30),
        'note': ''
    }
    assert parsed_items[0]['end'] == EXPECTED_END


def test_id():
    assert parsed_items[0]['id'] == 'chi_police/201712281830/25/beat_meeting_district_25'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_documents():
    assert parsed_items[0]['documents'] == []


def test_location():
    EXPECTED_LOCATION = [{
            'address': "St. Ferdinand's3115 N. Mason",
            'name': '',
            'neighborhood': ''
    }]
    assert parsed_items[0]['location'] == EXPECTED_LOCATION


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_sources():
    EXPECTED_SOURCES = [{'url': 'https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars',
                         'note': ''}]
    assert parsed_items[0]['sources'] == EXPECTED_SOURCES
