import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.cook_water import CookWaterSpider

freezer = freeze_time("2018-01-01")
freezer.start()

with open(join(dirname(__file__), "files", "cook_water.json"), "r") as f:
    test_response = json.load(f)

spider = CookWaterSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

parsed_items = [item for item in spider.parse_legistar(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board of Commissioners"


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 12, 20, 10, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "cook_water/201812201030/x/board_of_commissioners"


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "100 East Erie Street Chicago, IL 60611",
        "name": "Board Room",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://mwrd.legistar.com/DepartmentDetail.aspx?ID=1622&GUID=5E16B4CD-0692-4016-959D-3F080D6CFFB4"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[-2]["links"] == [
        {
            "href": "https://mwrd.legistar.com/View.ashx?M=M&ID=568714&GUID=86687153-30DD-4187-BFA9-8EB20EE3A570",  # noqa
            "title": "Minutes",
        },
        {
            "href": "https://mwrd.legistar.com/Video.aspx?Mode=Granicus&ID1=445&Mode2=Video",  # noqa
            "title": "Video",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_title_not_study_session(item):
    assert item["title"] != "Study Session"


def test_status():
    assert parsed_items[-1]["status"] == PASSED


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
