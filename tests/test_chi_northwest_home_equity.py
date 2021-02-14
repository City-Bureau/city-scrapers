from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_northwest_home_equity import ChiNorthwestHomeEquitySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_northwest_home_equity.html"),
    url="https://nwheap.com/category/meet-minutes-and-agendas/",
)
spider = ChiNorthwestHomeEquitySpider()

freezer = freeze_time("2021-02-12")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


# def test_tests():
#     print("Please write some tests for this spider or at least disable this one.")
#     assert True


def test_title():
    assert (
        parsed_items[0]["title"] == "Governing Commissioners Public Meeting"
        or "Board Meeting"
    )


def test_description():
    assert (
        parsed_items[0]["description"] == "Upcoming Events"
        if parsed_items[0]["title"].startswith("Governing")
        else "Past Meetings"
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 2, 18, 18, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2021, 2, 18, 19, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_northwest_home_equity/202102181830/x/ \
            governing_commissioners_public_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "",
        "name": "Meeting place not mentioned",
    }


def test_source():
    assert parsed_items[0]["source"] == test_response.url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://nwheap.com/events/governing-commissioners-public-meeting/",
            "title": "Governing Commissioners Public Meeting",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
