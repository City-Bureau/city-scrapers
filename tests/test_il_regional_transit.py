from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_regional_transit import IlRegionalTransitSpider

upcoming_response = file_response(
    join(dirname(__file__), "files", "il_regional_transit_upcoming.html"),
    url="https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials",
)


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
        upcoming_section = upcoming_response.css(
            ".bg-rtadarkgray-500.w-full.grid.grid-cols-1.p-8.mb-12.border-t-4.border-rtayellow-500"  # noqa
        )
        past_response.meta["upcoming_section"] = upcoming_section
        return [item for item in spider.parse(past_response)]


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Board Meeting"
    assert parsed_items[3]["title"] == "Pension Board of Trustees"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""
    assert parsed_items[3]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 3, 19, 9)
    assert parsed_items[3]["start"] == datetime(2026, 2, 26, 0)


def test_end_time(parsed_items):
    assert parsed_items[0]["end"] is None
    assert parsed_items[3]["end"] is None


def test_time_notes(parsed_items):
    assert (
        parsed_items[0]["time_notes"]
        == "Check the source page to confirm details on meeting time and location."
    )
    assert (
        parsed_items[3]["time_notes"]
        == "Check the source page to confirm details on meeting time and location."
    )


def test_id(parsed_items):
    assert parsed_items[0]["id"] == "il_regional_transit/202603190900/x/board_meeting"
    assert (
        parsed_items[3]["id"]
        == "il_regional_transit/202602260000/x/pension_board_of_trustees"
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[3]["status"] == PASSED


def test_links(parsed_items):
    assert parsed_items[0]["links"] == []
    assert parsed_items[3]["links"] == [
        {
            "href": "https://www.rtachicago.org/uploads/files/meeting-materials/RTA-Trustee-Meeting-Agenda-February-26-2026-draft.pdf-final.pdf",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[3]["classification"] == BOARD


def test_all_day(parsed_items):
    assert parsed_items[0]["all_day"] is False
    assert parsed_items[3]["all_day"] is False


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "Board Room, 16th Floor",
        "address": "175 W. Jackson Blvd., Chicago, IL 60604",
    }
    assert parsed_items[3]["location"] == {
        "name": "RTA Headquarters",
        "address": "175 W. Jackson Blvd., Chicago, IL 60604",
    }


def test_sources(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials"  # noqa
    )
    assert (
        parsed_items[3]["source"]
        == "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials"  # noqa
    )
