from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMITTEE,
    PASSED,
    TENTATIVE,
)
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.il_regional_transit import IlRegionalTransitSpider

freezer = freeze_time("2018-07-01")
freezer.start()
upcoming_response = file_response(
    join(dirname(__file__), "files", "il_regional_transit_upcoming.html"),
    url="http://rtachicago.granicus.com/ViewPublisher.php?view_id=5",
)
past_response = file_response(
    join(dirname(__file__), "files", "il_regional_transit_past.html"),
    url="http://rtachicago.granicus.com/ViewPublisher.php?view_id=4",
)

spider = IlRegionalTransitSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

parsed_items = [item for item in spider.parse(upcoming_response)] + [
    item for item in spider.parse(past_response)
]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 6, 21, 9)


def test_end_time():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert (
        parsed_items[0]["time_notes"]
        == "Initial meetings begin at 9:00am, with other daily meetings following"
    )


def test_id():
    assert (
        parsed_items[0]["id"] == "il_regional_transit/201806210900/x/board_of_directors"
    )


def test_status():
    assert parsed_items[10]["status"] == TENTATIVE
    assert parsed_items[-1]["status"] == PASSED


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[1]["links"] == [
        {
            "href": "http://rtachicago.granicus.com/AgendaViewer.php?view_id=5&event_id=325",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[1]["classification"] == COMMITTEE


def test_parse_classification():
    assert spider._parse_classification("Board of Directors") == BOARD
    assert spider._parse_classification("Audit Committee") == COMMITTEE
    assert (
        spider._parse_classification("Citizens Advisory Committee")
        == ADVISORY_COMMITTEE
    )
    assert (
        spider._parse_classification("Citizens Advisory Council") == ADVISORY_COMMITTEE
    )
    assert spider._parse_classification("Citizens Advisory Board") == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == spider.location


@pytest.mark.parametrize("item", parsed_items)
def test_sources(item):
    assert (
        item["source"]
        == "https://rtachicago.org/about-us/board-meetings/meetings-archive"
    )
