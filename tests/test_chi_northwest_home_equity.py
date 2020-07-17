import re
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_northwest_home_equity import ChiNorthwestHomeEquitySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_northwest_home_equity.html"),
    url="https://nwheap.com/category/meet-minutes-and-agendas/",
)
spider = ChiNorthwestHomeEquitySpider()

freezer = freeze_time("2020-06-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board Meeting"


def test_description():
    assert type(parsed_items[0]["description"]) == str


def test_start():
    assert type(parsed_items[0]["start"]) == datetime


def test_end():
    assert type(parsed_items[0]["start"]) == datetime


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_location():
    assert parsed_items[0]["location"]["address"] in spider.location_dict.values()


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://nwheap.com/category/meet-minutes-and-agendas/"
    )


def test_links():
    pass_test = False
    for item in parsed_items:
        if re.match(r"https://nwheap.com/wp-content/*", item["links"][0]["href"]):
            pass_test = True
    assert pass_test


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
