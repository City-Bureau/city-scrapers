from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_general_retirement_system import DetGeneralRetirementSystemSpider

test_response = file_response(
    join(dirname(__file__), "files", "det_general_retirement_system.html"),
    url='http://www.rscd.org/member_resources_/board_of_trustees/upcoming_meetings.php'
)
test_past_response = file_response(
    join(dirname(__file__), "files", "det_general_retirement_system_past.html"),
    url='http://www.rscd.org/member_resources_/board_of_trustees/past_meeting_agendas___minutes.php'
)

spider = DetGeneralRetirementSystemSpider()
freezer = freeze_time('2019-04-05')
freezer.start()
spider._parse_past_documents(test_past_response)
parsed_items = [item for item in spider._parse_meetings(test_response)]
freezer.stop()


def test_total():
    assert len(parsed_items) == 103


def test_title():
    assert parsed_items[0]['title'] == 'Board of Trustees'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2019, 1, 9, 10, 0)
    assert parsed_items[-1]['start'].year < 2019


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'] == 'det_general_retirement_system/201901091000/x/board_of_trustees'


def test_status():
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[8]['status'] == TENTATIVE


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'Retirement Systems Conference Room',
        'address': '500 Woodward Ave. Suite 300 Detroit, MI 48226'
    }
    assert parsed_items[-1]['location'] == {
        'name': 'Retirement Systems',
        'address': '500 Woodward Ave. Suite 300 Detroit, MI 48226'
    }


def test_source():
    assert parsed_items[0][
        'source'] == 'http://www.rscd.org/member_resources_/board_of_trustees/upcoming_meetings.php'


def test_links():
    assert parsed_items[0]['links'] == [{
        'href': 'http://www.rscd.org/GCA_4225_010919.pdf',
        'title': 'Agenda'
    }, {
        'href': 'http://www.rscd.org/4225_GCM_01092019.pdf',
        'title': 'Minutes'
    }]
    assert parsed_items[8]['links'] == []


def test_classification():
    assert parsed_items[0]['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False
