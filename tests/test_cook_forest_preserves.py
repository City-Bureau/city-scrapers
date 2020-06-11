import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED, TENTATIVE
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.cook_forest_preserves import CookForestPreservesSpider

freezer = freeze_time("2018-12-19")
freezer.start()

with open(join(dirname(__file__), "files", "cook_forest_preserve.json"), "r") as f:
    test_response = json.load(f)

spider = CookForestPreservesSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

parsed_items = [item for item in spider.parse_legistar(test_response)]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "FPD Board of Commissioners"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 12, 17, 10)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "cook_forest_preserves/201912171000/x/fpd_board_of_commissioners"
    )


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[30]["classification"] == COMMITTEE


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[20]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "Cook County Building, Board Room 118 North Clark Street, Chicago, Illinois",  # noqa
    }


def test_sources():
    assert (
        parsed_items[0]["source"]
        == "https://fpdcc.legistar.com/DepartmentDetail.aspx?ID=24752&GUID=714693C0-DBCE-4D3B-A3D9-A5FCBE27378B"  # noqa
    )  # noqa


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[20]["links"] == [
        {
            "href": "https://fpdcc.legistar.com/View.ashx?M=A&ID=584806&GUID=C00EFBA7-F086-41D9-B0EE-A9057114D3EE",  # noqa
            "title": "Agenda",
        },
        {
            "title": "Video",
            "href": "https://fpdcc.legistar.com/Video.aspx?Mode=Granicus&ID1=437&Mode2=Video",  # noqa
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
