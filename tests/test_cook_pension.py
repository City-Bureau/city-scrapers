from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_pension import CookPensionSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_pension.html"),
    url="https://www.cookcountypension.com/agendaminutes/",
)
spider = CookPensionSpider()

freezer = freeze_time("2019-04-17")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)],
    key=lambda i: i["start"],
    reverse=True,
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 8


def test_title():
    assert parsed_items[0]["title"] == "Retirement Board"
    assert parsed_items[1]["title"] == "Health Benefits Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 4, 4, 9, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm times"


def test_id():
    assert parsed_items[0]["id"] == "cook_pension/201904040930/x/retirement_board"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"] == "https://www.cookcountypension.com/agendaminutes/"
    )


def test_links():
    assert parsed_items[3]["links"] == [
        {
            "href": "https://www.cookcountypension.com/assets/1/6/030719_Board_Agenda.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www.cookcountypension.com/assets/1/6/Board_Minutes_030719.pdf",  # noqa
            "title": "Minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[1]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
