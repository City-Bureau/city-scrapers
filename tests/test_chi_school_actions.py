from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import FORUM
from city_scrapers_core.utils import file_response

from city_scrapers.spiders.chi_school_actions import ChiSchoolActionsSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_school_actions.html"),
    url="http://schoolinfo.cps.edu/SchoolActions/Documentation.aspx",
)
spider = ChiSchoolActionsSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_count():
    assert len(parsed_items) == 33


def test_title():
    assert (
        parsed_items[0]["title"]
        == "School Actions: Castellanos - Cardenas Community Meetings: Consolidation"
    )


def test_classification():
    assert parsed_items[0]["classification"] == FORUM


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 1, 9, 18)


def test_end():
    assert parsed_items[0]["end"] == datetime(2018, 1, 9, 20)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_school_actions/201801091800/x/school_actions_castellanos_cardenas_community_meetings_consolidation"  # noqa
    )


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Rosario Castellanos ES",
        "address": "2524 S Central Park Ave Chicago, IL",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://schoolinfo.cps.edu/SchoolActions/Documentation.aspx"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Transition Plan",
            "href": "http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=5247",
        },
        {
            "title": "Transition Plan - ELL",
            "href": "http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=5248",
        },
        {
            "title": "Parent Letter",
            "href": "http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=5243",
        },
        {
            "title": "Parent Letter - ELL",
            "href": "http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=6298",
        },
        {
            "title": "Staff Letter",
            "href": "http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=5245",
        },
        {
            "title": "Staff Letter - ELL",
            "href": "http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=6306",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""
