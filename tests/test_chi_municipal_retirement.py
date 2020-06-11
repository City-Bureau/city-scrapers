from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_municipal_retirement import ChiMunicipalRetirementSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_municipal_retirement.html"),
    url="https://www.meabf.org/retirement-board/minutes",
)
spider = ChiMunicipalRetirementSpider()

freezer = freeze_time("2019-04-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 5


def test_title():
    assert parsed_items[0]["title"] == "Retirement Board"
    assert parsed_items[1]["title"] == "Investment Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 4, 18, 9)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm time"


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_municipal_retirement/201904180900/x/retirement_board"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[1]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "https://www.meabf.org/retirement-board/minutes"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.meabf.org/assets/pdfs/meetings/agenda/Posted_Agenda_2019-04_REVISED2.pdf",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[1]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
