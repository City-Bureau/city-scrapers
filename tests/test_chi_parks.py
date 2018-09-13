import pytest
import json
from datetime import date, time

from freezegun import freeze_time
from city_scrapers.constants import BOARD
from city_scrapers.spiders.chi_parks import ChiParksSpider

freezer = freeze_time('2018-01-01 12:00:01')
freezer.start()
test_response = []
with open('tests/files/chi_parks.txt') as f:
    for line in f:
        test_response.append(json.loads(line))
spider = ChiParksSpider()
parsed_items = [item for item in spider._parse_events(test_response)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Board of Commissioners'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    EXPECTED_START = {
        'date': date(2017, 12, 13),
        'time': time(15, 30),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START


def test_end():
    EXPECTED_END = {
        'date': date(2017, 12, 13),
        'time': time(18, 30),
        'note': 'Estimated 3 hours after start time'
    }
    assert parsed_items[0]['end'] == EXPECTED_END


def test_id():
    assert parsed_items[0]['id'] == (
        'chi_parks/201712131530/x/board_of_commissioners'
    )


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == BOARD


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    EXPECTED_LOCATION = {
        'address': (
            'Board Room ADMINISTRATION BUILDING AT 541 '
            'NORTH FAIRBANKS COURT, CHICAGO, ILLINOIS 60611 '
            '8TH FLOOR BOARD ROOM'
        ),
        'name': '',
        'neighborhood': ''
    }
    assert parsed_items[1]['location'] == EXPECTED_LOCATION


def test_documents():
    EXPECTED_DOCUMENTS = [
        {
            'url': (
                'https://chicagoparkdistrict.legistar.com/'
                'MeetingDetail.aspx?ID=521450&GUID=4D888BE3-BD28-'
                '4F58-AEE3-76627090F26D&Options=info&Search='
            ),
            'note': 'Meeting Details'
        },
        {
            'url': (
                'https://chicagoparkdistrict.legistar.com/'
                'View.ashx?M=A&ID=521450&GUID=4D888BE3-BD28-'
                '4F58-AEE3-76627090F26D'
            ),
            'note': 'Agenda'
        }
    ]
    assert parsed_items[2]['documents'] == EXPECTED_DOCUMENTS


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'


def test_sources():
    EXPECTED_SOURCES = [{
        'note': '',
        'url': 'https://chicagoparkdistrict.legistar.com/Calendar.aspx'
    }]
    assert parsed_items[0]['sources'] == EXPECTED_SOURCES
