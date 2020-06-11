from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_18 import ChiSsa18Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_18.html"),
    url="https://northalsted.com/community/",
)
spider = ChiSsa18Spider()

freezer = freeze_time("2020-01-28")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 2, 5, 9, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2020, 2, 5, 10, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_18/202002050900/x/commission"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Center on Halsted",
        "address": "3656 N Halsted St, Conference Room 200, Chicago IL 60613",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://northalsted.com/community/"


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_date():
    assert parsed_items[0]["all_day"] is False
