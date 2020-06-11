from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_29 import ChiSsa29Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_29.html"),
    url="http://www.westtownssa.org/transparency/",
)
spider = ChiSsa29Spider()

freezer = freeze_time("2019-07-02")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)], key=itemgetter("start")
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 23


def test_title():
    assert parsed_items[0]["title"] == "Commission"
    assert parsed_items[14]["title"] == "Special Audit Review Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 1, 4, 11, 0)
    assert parsed_items[14]["start"] == datetime(2019, 4, 29, 14)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_29/201801041100/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "http://www.westtownssa.org/transparency/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Minutes",
            "href": "http://www.westtownssa.org/content/directory/attachments/events/e/elsrmc/1.4.18 Minutes.pdf",  # noqa
        }
    ]
    assert parsed_items[-1]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
