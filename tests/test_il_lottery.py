from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_lottery import IlLotterySpider

test_response = file_response(
    join(dirname(__file__), "files", "il_lottery.html"),
    url="https://www.illinoislottery.com/illinois-lottery/lottery-control-board",
)
spider = IlLotterySpider()

freezer = freeze_time("2019-08-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_len():
    assert len(parsed_items) == 24


def test_title():
    assert parsed_items[0]["title"] == "Lottery Control Board Quarterly Meeting"
    assert parsed_items[2]["title"] == "Lottery Control Board Special Meeting"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 11, 6, 13, 30)


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == ""


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[2]["status"] == PASSED


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "Chicago Lottery Office",
        "address": "122 South Michigan Avenue, 19th Floor, Chicago, IL 60603",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    source = "https://www.illinoislottery.com/illinois-lottery/lottery-control-board"
    assert item["source"] == source


def test_links():
    assert len(parsed_items[0]["links"]) == 0
    assert parsed_items[3]["links"] == [
        {
            "href": "https://www.illinoislottery.com/content/dam/il/pdfs/lottery-control-board/May%202019%20Lottery%20Control%20Board%20Meeting%20Agenda.pdf",  # noqa
            "title": "Illinois Lottery Control Board Meeting Agenda - May 15, 2019",
        }
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
