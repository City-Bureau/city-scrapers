from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, PASSED
from tests.utils import file_response

from city_scrapers.spiders.cook_county import CookCountySpider

test_response = file_response(
    'files/cook_county_event.html',
    url='https://www.cookcountyil.gov/event/cook-county-zoning-building-committee-6'
)
spider = CookCountySpider()
item = spider._parse_event(test_response)


def test_title():
    assert item['title'] == 'ZBA Public Hearing'


def test_start():
    assert item['start'] == datetime(2017, 11, 15, 13)


def test_end():
    assert item['end'] == datetime(2017, 11, 15, 15)


def test_time_notes():
    assert item['time_notes'] == ''


def test_id():
    assert item['id'] == 'cook_county/201711151300/x/zba_public_hearing'


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert spider._parse_classification('Board of Commissioners') == BOARD
    assert spider._parse_classification(
        'Economic Development Advisory Committee'
    ) == ADVISORY_COMMITTEE
    assert spider._parse_classification('Finance Committee') == COMMITTEE
    assert spider._parse_classification('Finance Subcommittee on Litigation') == COMMITTEE
    assert spider._parse_classification('Finance Subcommittee on Workers Compensation') == COMMITTEE
    assert spider._parse_classification(
        'Committee of Suburban Cook County Commissioners - PACE'
    ) == COMMITTEE
    assert spider._parse_classification('Rules & Administration Committee') == COMMITTEE
    assert spider._parse_classification('Roads & Bridges Committee') == COMMITTEE
    assert spider._parse_classification('Zoning & Building Committee') == COMMITTEE
    assert spider._parse_classification('Justice Advisory Council') == ADVISORY_COMMITTEE
    assert spider._parse_classification('JAC Council Meeting') == ADVISORY_COMMITTEE


def test_status():
    assert item['status'] == PASSED


def test_location():
    assert item['location'] == {
        'name': '',
        'address': '69 W. Washington Street Chicago , IL  60602',
    }


def test_sources():
    assert item['source'
                ] == 'https://www.cookcountyil.gov/event/cook-county-zoning-building-committee-6'


def test_description():
    assert item['description'] == (
        'Public Hearing '
        'A public hearing has been scheduled for the Cook County Zoning Board of Appeals on '
        'Wednesday, November 15, 2017, 1:00PM at '
        '69 W. Washington, 22nd Floor Conference Room, Chicago, Illinois 60602.'
    )


def test_links():
    assert item['links'] == [{
        'href': 'https://www.cookcountyil.gov/sites/default/files/zba_november_15_agenda.pdf',
        'title': 'ZBA 11-15-2017 Agenda'
    }]
