from datetime import datetime
from os.path import dirname, join
from unittest.mock import MagicMock

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

JANUARY_IDX = 0
NOVEMBER_IDX = 10


@pytest.fixture
def parsed_items(monkeypatch):
    mock_res = MagicMock()
    mock_res.return_value.status_code = 404
    monkeypatch.setattr("requests.get", mock_res)
    freezer = freeze_time("2019-02-05")
    freezer.start()
    items = [item for item in spider.parse(test_response)]
    freezer.stop()
    return items


@pytest.fixture
def january_item(monkeypatch):
    mock_res = MagicMock()
    mock_res.return_value.status_code = 200
    monkeypatch.setattr("requests.get", mock_res)
    freezer = freeze_time("2019-02-05")
    freezer.start()
    items = [item for item in spider.parse(test_response)]
    freezer.stop()
    return items[0]


# There are 12 board meetings, one for each month
def test_12_board_meetings(parsed_items):
    assert sum(["board" in item["title"].lower() for item in parsed_items]) == 12


# Test all items have a start time
def test_start_exists(parsed_items):
    assert all(isinstance(item["start"], datetime) for item in parsed_items)


def test_title(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["title"] == "Board Meeting"


def test_all_day(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["all_day"] is False


def test_description(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["start"] == datetime(2019, 11, 13, 16, 30)


def test_end(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["end"] is None


def test_time_notes(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["time_notes"] is None


def test_id(parsed_items):
    assert (
        isinstance(parsed_items[NOVEMBER_IDX]["id"], str)
        and parsed_items[NOVEMBER_IDX]["id"] != ""
    )


def test_status(parsed_items):
    assert (
        isinstance(parsed_items[NOVEMBER_IDX]["status"], str)
        and parsed_items[NOVEMBER_IDX]["id"] != ""
    )


def test_location(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["location"] == {
        "name": "Pace Headquarters",
        "address": "550 W. Algonquin Rd., Arlington Heights, IL 60005",
    }


def test_source(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["source"] == (
        "http://www.pacebus.com/sub/news_events/calendar_of_events.asp"
    )


def test_classification(parsed_items):
    assert parsed_items[NOVEMBER_IDX]["classification"] == BOARD


# Test links
# January 2019 should have valid ones


def test_start_january(january_item):
    assert january_item["start"] == datetime(2019, 1, 16, 16, 30)


def test_links_january(january_item):
    assert january_item["links"] == [
        {
            "href": (
                "https://www.pacebus.com/pdf/Board_Minutes/"
                "Pace_Board_Meeting_Agenda_January_16_2019.pdf"
            ),
            "title": "Agenda",
        },
        {
            "href": (
                "https://www.pacebus.com/pdf/Board_Minutes/"
                "Pace_Board_Meeting_Minutes_Jan_2019.pdf"
            ),
            "title": "Minutes",
        },
    ]
