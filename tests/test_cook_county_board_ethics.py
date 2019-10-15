from datetime import datetime

from city_scrapers_core.constants import BOARD, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.cook_county_board_ethics import CookCountyBoardEthicsSpider

test_response = file_response(
    'files/cook_county_board_ethics_event.html',
    url='https://www.cookcountyil.gov/event/cook-county-board-ethics-meeting-3'
)
spider = CookCountyBoardEthicsSpider()

freezer = freeze_time("2019-10-9")
freezer.start()
item = spider._parse_event(test_response)
freezer.stop()


def test_title():
    assert item['title'] == 'Cook County: Board of Ethics Meeting'


def test_start():
    assert item['start'] == datetime(2019, 8, 29, 14)


def test_end():
    assert item['end'] == datetime(2019, 8, 29, 16)


def test_time_notes():
    assert item['time_notes'] == ''


def test_id():
    assert item['id'
                ] == 'cook_county_board_ethics/201908291400/x/cook_county_board_of_ethics_meeting'


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == BOARD


def test_status():
    assert item['status'] == PASSED


def test_location():
    assert item['location'] == {
        'name': '',
        'address': '69 W. Washington Street, Suite 3040 Chicago IL 60602',
    }


def test_sources():
    assert item['source'] == 'https://www.cookcountyil.gov/event/cook-county-board-ethics-meeting-3'


def test_description():
    assert item['description'] == ''


def test_links():
    assert item['links'] == []
