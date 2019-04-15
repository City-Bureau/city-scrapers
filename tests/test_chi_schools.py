from datetime import datetime

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from tests.utils import file_response

from city_scrapers.spiders.chi_schools import ChiSchoolsSpider

test_response = file_response(
    'files/cpsboe.html', url='http://www.cpsboe.org/meetings/planning-calendar'
)
spider = ChiSchoolsSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_event_count():
    assert len(parsed_items) == 14


def test_id():
    assert parsed_items[0]['id'] == 'chi_schools/201707261030/x/board_of_education'


def test_links():
    assert parsed_items[0]['links'] == []


def test_title():
    assert parsed_items[0]['title'] == 'Board of Education'


@pytest.mark.parametrize('item', parsed_items)
def test_source(item):
    assert item['source'] == 'http://www.cpsboe.org/meetings/planning-calendar'


@pytest.mark.parametrize('item', parsed_items)
def test_event_description(item):
    assert item['description'] == (
        'Advance registration will be open the Monday preceding the Board meeting at 10:30 a.m. '
        'and close Tuesday at 5:00 p.m., or until all slots are filled or otherwise noted.'
        '\xa0\xa0Advance registration is available for speakers and observers. You can advance '
        'register via: \n Online:  www.cpsboe.org \xa0(recommended) \n Phone:  (773)553-1600 \n '
        'In Person: 1 North Dearborn Street, Suite 950 \n Board meetings begin at 10:30 a.m., '
        'unless otherwise noted. The public participation segment of the meeting will begin at the '
        'time indicated on the meeting agenda and proceed for no more than 60 speaking slots for '
        'up to two hours. Further, let the official record reflect that the 2017-2018 Planning '
        'Calendar has been prepared in accordance with the  Illinois Open Meetings Act.'
    )


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


def test_start():
    assert parsed_items[0]['start'] == datetime(2017, 7, 26, 10, 30)


def test_end():
    assert parsed_items[0]['end'] is None


def test_time_notes():
    assert parsed_items[0]['time_notes'] == ''


def test_status():
    assert parsed_items[0]['status'] == PASSED


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'name': 'CPS Loop Office',
        'address': '42 W. Madison Street, Garden Level Chicago, IL 60602 Board Room',
    }
