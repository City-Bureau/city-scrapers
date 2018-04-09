import pytest
from tests.utils import file_response
from documenters_aggregator.spiders.chi_police import Chi_policeSpider

test_response = file_response('files/chi_police.json')
spider = Chi_policeSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == '2514 Beat Meeting'


def test_description():
    EXPECTED_DESCRIPTION = (
        "CPD Beat meetings, held on all 279 police "
        "beats in the City, provide a regular opportunity "
        "for police officers, residents, and other community "
        "stakeholders to exchange information, identify and "
        "prioritize problems, and begin developing solutions "
        "to those problems."
    )
    assert parsed_items[0]['description'] == EXPECTED_DESCRIPTION


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-12-28T18:30:00-06:00'


def test_end_time():
    assert parsed_items[0]['end_time'].isoformat() == '2017-12-28T19:30:00-06:00'


def test_id():
    assert parsed_items[0]['id'] == 'chi_police/201712281830/25/2514_beat_meeting'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'Beat Meeting'


def test_status():
    assert parsed_items[0]['status'] == 'confirmed'


def test_location():
    EXPECTED_LOCATION = {
            'url': None,
            'address': "St. Ferdinand's3115 N. Mason",
            'name': None,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
    }
    assert parsed_items[0]['location'] == EXPECTED_LOCATION


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_sources():
    EXPECTED_SOURCES = [{'url': 'https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars',
                         'note': ''}]
    assert parsed_items[0]['sources'] == EXPECTED_SOURCES


def test_timezone():
    assert parsed_items[0]['timezone'] == 'America/Chicago'
