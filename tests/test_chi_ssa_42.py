from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_ssa_42 import ChiSsa42Spider

freezer = freeze_time("2018-11-07")
freezer.start()
spider = ChiSsa42Spider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

res = file_response(
    join(dirname(__file__), "files", "chi_ssa_42.html"),
    url="https://ssa42.org/ssa-42-meeting-dates/",
)
minutes_res = file_response(
    join(dirname(__file__), "files", "chi_ssa_42_minutes.html"),
    url="https://ssa42.org/minutes-of-meetings/",
)
parsed_items = [item for item in spider._parse_meetings(res, upcoming=True)] + [
    item for item in spider._parse_meetings(minutes_res)
]
freezer.stop()


def test_count():
    assert len(parsed_items) == 12


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 11, 8, 18, 30)
    assert parsed_items[1]["start"] == datetime(2018, 9, 20, 18, 30)


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_42/201811081830/x/ssa_42_commission"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[-1]["status"] == PASSED


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[1]["links"] == [
        {
            "href": (
                "https://ssa42.org/wp-content/uploads/sites/6/2018/"
                "09/SSAMeetingAgendaSeptember202018.pdf"
            ),
            "title": "Agenda",
        },
        {
            "href": (
                "https://ssa42.org/wp-content/uploads/sites/6/2018/"
                "11/SSAMEETINGMINUTES_Sep202018.pdf"
            ),
            "title": "Minutes",
        },
    ]


def test_title():
    assert parsed_items[0]["title"] == "SSA #42 Commission"
    assert parsed_items[4]["title"] == "SSA #42 Commission - Closed Meeting"


def test_source():
    assert parsed_items[0]["source"] == "https://ssa42.org/ssa-42-meeting-dates/"
    assert parsed_items[-1]["source"] == "https://ssa42.org/minutes-of-meetings/"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == spider.location


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
