from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_housing import CookHousingSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_housing.html"),
    url="http://thehacc.org/events/",
)
spider = CookHousingSpider()

freezer = freeze_time("2019-10-03")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 2


def test_title():
    assert parsed_items[0]["title"] == "Board of Commissioners"
    assert parsed_items[1]["title"] == "Board of Commissioners"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 10, 17, 14, 0)
    assert parsed_items[1]["start"] == datetime(2019, 12, 12, 14, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 10, 17, 16, 0)
    assert parsed_items[1]["end"] == datetime(2019, 12, 12, 16, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[1]["time_notes"] == ""


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[1]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "HACC Downtown",
        "address": "175 W Jackson Blvd, Chicago, IL"
    }
    assert parsed_items[1]["location"] == {
        "name": "HACC Downtown",
        "address": "175 W Jackson Blvd, Chicago, IL"
    }


def test_source():
    assert parsed_items[0]["source"] == \
        "http://thehacc.org/event/housing-authority-of-cook-county-board-meeting-2-2-2-2-4/"
    assert parsed_items[1]["source"] == \
        "http://thehacc.org/event/housing-authority-of-cook-county-board-meeting-2-2-2-2-5/"


@pytest.mark.parametrize("item", parsed_items)
def test_links(item):
    assert item["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[1]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
