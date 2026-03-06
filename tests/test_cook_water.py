import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.cook_water import CookWaterSpider

freezer = freeze_time("2026-03-01")
freezer.start()

with open(join(dirname(__file__), "files", "cook_water.json"), "r") as f:
    test_response = json.load(f)

spider = CookWaterSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

parsed_items = [item for item in spider.parse_legistar(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 23


def test_title():
    assert parsed_items[19]["title"] == "Board of Commissioners"


def test_start():
    assert parsed_items[19]["start"] == datetime(2026, 2, 19, 10, 30)


def test_end():
    assert parsed_items[19]["end"] is None


def test_id():
    assert parsed_items[19]["id"] == "cook_water/202602191030/x/board_of_commissioners"


def test_status():
    assert parsed_items[19]["status"] == PASSED


def test_classification():
    assert parsed_items[19]["classification"] == BOARD


def test_location():
    assert parsed_items[19]["location"] == {
        "address": "100 East Erie Street Chicago, IL 60611",
        "name": "Board Room",
    }


def test_source():
    assert (
        parsed_items[19]["source"]
        == "https://mwrd.legistar.com/DepartmentDetail.aspx?ID=1622&GUID=5E16B4CD-0692-4016-959D-3F080D6CFFB4"  # noqa
    )


def test_links():
    assert parsed_items[19]["links"] == [
        {
            "href": "https://mwrd.legistar.com/View.ashx?M=A&ID=1345714&GUID=4772CE57-A2D1-46EB-BDB5-AB39CFF45A40",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://mwrd.legistar.com/View.ashx?M=M&ID=1345714&GUID=4772CE57-A2D1-46EB-BDB5-AB39CFF45A40",  # noqa
            "title": "Minutes",
        },
        {
            "href": "https://mwrd.legistar.com/Video.aspx?Mode=Granicus&ID1=1161&Mode2=Video",  # noqa
            "title": "Video",
        },
        {
            "href": "https://mwrd.legistar.com/MeetingDetail.aspx?ID=1345714&GUID=4772CE57-A2D1-46EB-BDB5-AB39CFF45A40&Options=info|&Search=",  # noqa
            "title": "Meeting Details",
        },
        {
            "href": "https://mwrd.legistar.com/View.ashx?M=AADA&ID=1345714&GUID=4772CE57-A2D1-46EB-BDB5-AB39CFF45A40",  # noqa
            "title": "Accessible Agenda",
        },
        {
            "href": "https://mwrd.legistar.com/View.ashx?M=MADA&ID=1345714&GUID=4772CE57-A2D1-46EB-BDB5-AB39CFF45A40",  # noqa
            "title": "Accessible Minutes",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_title_not_study_session(item):
    assert item["title"] != "Study Session"


def test_tentative_status():
    assert parsed_items[0]["status"] == TENTATIVE


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
