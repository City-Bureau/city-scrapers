from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_sports_facilities_authority import (
    IlSportsFacilitiesAuthoritySpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "il_sports_facilities_authority.html"),
    url="https://www.isfauthority.com/governance/board-meetings/",
)
spider = IlSportsFacilitiesAuthoritySpider()

freezer = freeze_time("2020-10-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 40


def test_title():
    assert parsed_items[1]["title"] == "Board Meeting"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[1]["start"] == datetime(2020, 9, 17, 0, 0)


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "Authority offices",
        "address": "Guaranteed Rate Field, 333 West 35th Street, Chicago, IL",
    }


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[1]["classification"] == BOARD
    assert parsed_items[5]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
