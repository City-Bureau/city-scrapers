from datetime import datetime

from city_scrapers_core.constants import PASSED, POLICE_BEAT
from tests.utils import file_response

from city_scrapers.spiders.chi_police import ChiPoliceSpider

test_response = file_response('files/chi_police.json')
spider = ChiPoliceSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_title():
    assert parsed_items[0]['title'] == 'CAPS District 25, Beat 14'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2017, 12, 28, 18, 30)


def test_end_time():
    assert parsed_items[0]['end'] == datetime(2017, 12, 28, 19, 30)


def test_id():
    assert parsed_items[0]['id'] == 'chi_police/201712281830/25/caps_district_25_beat_14'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_classification():
    assert parsed_items[0]['classification'] == POLICE_BEAT


def test_links():
    assert parsed_items[0]['links'] == []


def test_location():
    EXPECTED_LOCATION = {
        'address': "St. Ferdinand's3115 N. Mason Chicago, IL",
        'name': '',
    }
    assert parsed_items[0]['location'] == EXPECTED_LOCATION


def test_source():
    assert parsed_items[0][
        'source'
    ] == 'https://home.chicagopolice.org/office-of-community-policing/community-event-calendars/'  # noqa
