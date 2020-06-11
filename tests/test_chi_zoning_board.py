from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_zoning_board import ChiZoningBoardSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_zoning_board.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/zoning_board_of_appeals.html",  # noqa
)
spider = ChiZoningBoardSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2018-01-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_meeting_count():
    assert len(parsed_items) == 24


def test_unique_id_count():
    assert len(set([item["id"] for item in parsed_items])) == 24


def test_title():
    assert parsed_items[0]["title"] == "Board of Appeals"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 1, 19, 9)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_zoning_board/201801190900/x/board_of_appeals"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Hall",
        "address": "121 N LaSalle St Chicago, IL 60602",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.chicago.gov/city/en/depts/dcd/supp_info/zoning_board_of_appeals.html"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Administrative_Reviews_and_Approvals/Agendas/ZBA_Jan_2018_Minutes_rev.pdf",  # noqa
            "title": "Minutes",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Administrative_Reviews_and_Approvals/Agendas/ZBA_Jan_2018_Map.pdf",  # noqa
            "title": "Map",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
