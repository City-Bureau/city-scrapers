import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_parks import ChiParksSpider

freezer = freeze_time("2018-01-01")
freezer.start()

with open(join(dirname(__file__), "files", "chi_parks.json")) as f:
    test_response = json.load(f)

spider = ChiParksSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

parsed_items = [item for item in spider.parse_legistar(test_response)]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board of Commissioners"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2017, 12, 13, 15, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Estimated 2 hour duration"


def test_id():
    assert parsed_items[0]["id"] == "chi_parks/201712131530/x/board_of_commissioners"


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[1]["location"] == {
        "address": (
            "Board Room ADMINISTRATION BUILDING AT 541 "
            "NORTH FAIRBANKS COURT, CHICAGO, ILLINOIS 60611 "
            "8TH FLOOR BOARD ROOM"
        ),
        "name": "",
    }


def test_links():
    assert parsed_items[2]["links"] == [
        {
            "href": "https://chicagoparkdistrict.legistar.com/View.ashx?M=A&ID=521450&GUID=4D888BE3-BD28-4F58-AEE3-76627090F26D",  # noqa
            "title": "Agenda",
        },
    ]


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://chicagoparkdistrict.legistar.com/Calendar.aspx"
    )
