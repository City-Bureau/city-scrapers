import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, TENTATIVE
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.cook_board import CookBoardSpider

freezer = freeze_time("2017-09-01")
freezer.start()

with open(join(dirname(__file__), "files", "cook_board.json"), "r") as f:
    test_response = json.load(f)

spider = CookBoardSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

parsed_items = [item for item in spider.parse_legistar(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 82


def test_title():
    assert parsed_items[25]["title"] == "Board of Commissioners"


def test_description():
    assert parsed_items[25]["description"] == ""


def test_start():
    assert parsed_items[25]["start"] == datetime(2017, 9, 13, 11)


def test_end():
    assert parsed_items[25]["end"] is None


def test_id():
    assert parsed_items[25]["id"] == "cook_board/201709131100/x/board_of_commissioners"


def test_classification():
    assert parsed_items[25]["classification"] == BOARD


def test_status():
    assert parsed_items[25]["status"] == TENTATIVE


def test_location():
    assert parsed_items[25]["location"] == {
        "name": "",
        "address": "Cook County Building, Board Room, 118 North Clark Street, Chicago, Illinois",  # noqa
    }


def test_source():
    assert (
        parsed_items[25]["source"]
        == "https://cook-county.legistar.com/DepartmentDetail.aspx?ID=20924&GUID=B78A790A-5913-4FBF-8FBF-ECEE445B7796"  # noqa
    )  # noqa


def test_links():
    assert parsed_items[25]["links"] == [
        {
            "href": "https://cook-county.legistar.com/View.ashx?M=A&ID=521583&GUID=EA23CB0D-2E10-47EA-B4E2-EC7BA3CB8D76",  # noqa
            "title": "Agenda",
        },
        {
            "title": "Video",
            "href": "https://cook-county.legistar.comVideo.aspx?Mode=Granicus&ID1=1858&Mode2=Video",  # noqa
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
