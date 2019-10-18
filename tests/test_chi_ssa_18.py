import os
from datetime import datetime

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_18 import ChiSsa18Spider

test_response = file_response(
    # join(dirname(__file__), "files", "chi_ssa_18.html"),
    # url="https://northalsted.com/community/",
    os.path.dirname(__file__).join("files", "chi_ssa_18.html")
)
spider = ChiSsa18Spider()
freezer = freeze_time("2019-10-04")
freezer.start()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_tests():
    print("Please write some tests for this spider or at least disable this one.")
    assert False


"""
Uncomment below
"""


def test_title():
    assert parsed_items[0]["title"] == "Community - Northalsted Business Alliance"


def test_description():
    assert parsed_items[
        0]["description"
           ] == """The first officially recognized gay village in the United States, Boystown in
    Chicago, Illinois is the commonly accepted nickname for the
    eclectic Lakeview neighborhood that is
    home to Chicago’s visible and active LGBT community.
    Boystown is situated just east of Wrigleyville."""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 12, 4)


def test_end():
    assert parsed_items[0]["end"] == "None"


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == ""


def test_status():
    assert parsed_items[0]["status"] == ""


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "3656 N Halsted Street, Chicago, IL 60613",
        "name": "Center on Halsted"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://northalsted.com/community/"


@pytest.mark.parametrize('item', 'response')
def test_links():
    assert parsed_items[0]["links"] == [{"href": 'response'.url, "title": "Minutes"}]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
