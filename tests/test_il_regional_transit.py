from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_regional_transit import IlRegionalTransitSpider

past_response = file_response(
    join(dirname(__file__), "files", "il_regional_transit_past.html"),
    url="https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials?year=2026",  # noqa
)


@pytest.fixture
def spider():
    return IlRegionalTransitSpider()


@pytest.fixture
def parsed_items(spider):
    with freeze_time("2026-03-13"):
        return [item for item in spider.parse(past_response)]


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Pension Board of Trustees"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 2, 26, 0)


def test_end_time(parsed_items):
    assert parsed_items[0]["end"] is None


def test_time_notes(parsed_items):
    assert (
        parsed_items[0]["time_notes"]
        == "Check the source page to confirm details on meeting time and location."
    )


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"]
        == "il_regional_transit/202602260000/x/pension_board_of_trustees"
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == PASSED


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.rtachicago.org/uploads/files/meeting-materials/RTA-Trustee-Meeting-Agenda-February-26-2026-draft.pdf-final.pdf",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD


def test_all_day(parsed_items):
    assert parsed_items[0]["all_day"] is False


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "RTA Headquarters",
        "address": "175 W. Jackson Blvd., Chicago, IL 60604",
    }


def test_sources(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials"  # noqa
    )
