from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_pace_board import CookPaceBoardSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_pace_board.html"),
    url="http://www.pacebus.com/sub/news_events/calendar_of_events.asp",
)
spider = CookPaceBoardSpider()

freezer = freeze_time("2019-02-05")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


# There are 12 board meetings, one for each month
def test_12_board_meetings():
    assert sum(["board" in item["title"].lower() for item in parsed_items]) == 12


# Test all items have a start time
@pytest.mark.parametrize("item", parsed_items)
def test_start_exists(item):
    assert isinstance(item['start'], datetime)


# VALUE TEST FOR NOVEMBER MEETING #

november_item = parsed_items[10]


def test_title():
    assert november_item["title"] == "Board Meeting"


def test_all_day():
    assert november_item["all_day"] is False


def test_description():
    assert november_item["description"] == ""


def test_start():
    assert november_item["start"] == datetime(2019, 11, 13, 16, 30)


def test_end():
    assert november_item["end"] is None


def test_time_notes():
    assert november_item["time_notes"] is None


def test_id():
    assert isinstance(november_item["id"], str) and november_item["id"] != ""


def test_status():
    assert isinstance(november_item["status"], str) and november_item["id"] != ""


def test_location():
    assert november_item["location"] == {
        "name": "Pace Headquarters",
        "address": "550 W. Algonquin Rd., Arlington Heights, IL 60005"
    }


def test_source():
    assert november_item["source"] == (
        "http://www.pacebus.com/sub/news_events/calendar_of_events.asp"
    )


def test_classification():
    assert november_item["classification"] == BOARD


# Test links
# January 2019 should have valid ones
january_item = parsed_items[0]


def test_start_january():
    assert january_item["start"] == datetime(2019, 1, 16, 16, 30)


def test_links_january():
    assert january_item["links"] == [
        {
            "href": (
                "https://www.pacebus.com/pdf/Board_Minutes/"
                "Pace_Board_Meeting_Agenda_January_16_2019.pdf"
            ),
            "title": "Agenda"
        },
        {
            "href": (
                "https://www.pacebus.com/pdf/Board_Minutes/"
                "Pace_Board_Meeting_Minutes_Jan_2019.pdf"
            ),
            "title": "Minutes"
        },
    ]
