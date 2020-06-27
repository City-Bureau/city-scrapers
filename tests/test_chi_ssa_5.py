from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_5 import ChiSsa5Spider

spider = ChiSsa5Spider()

freezer = freeze_time("2018-10-12")
freezer.start()
minutes_req = file_response(
    join(dirname(__file__), "files", "chi_ssa_5_minutes.html"),
    url="http://scpf-inc.org/ssa5/meeting-minutes/",
)
spider.meetings = spider._parse_current_year(
    file_response(
        join(dirname(__file__), "files", "chi_ssa_5.html"),
        url="http://scpf-inc.org/ssa5/meeting-calendar/",
    )
)
parsed_items = [item for item in spider._parse_minutes(minutes_req)]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Regular Commission"
    assert parsed_items[4]["title"] == "Special Commission"


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 1, 25, 14)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_5/201801251400/x/regular_commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[13]["status"] == TENTATIVE
    assert parsed_items[-1]["status"] == PASSED


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://scpf-inc.org/wp-content/uploads/2018/04/January-Agenda.pdf",
            "title": "Agenda",
        },
        {
            "href": "http://scpf-inc.org/wp-content/uploads/2018/04/SSA-Meeting-Minutes-January-25-2018.pdf",  # noqa
            "title": "Minutes",
        },
    ]
    assert parsed_items[11]["links"] == []


def test_source():
    assert parsed_items[0]["source"] == "http://scpf-inc.org/ssa5/meeting-calendar/"
    assert parsed_items[-1]["source"] == "http://scpf-inc.org/ssa5/meeting-minutes/"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == spider.location


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
