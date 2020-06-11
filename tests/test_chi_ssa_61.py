from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_61 import ChiSsa61Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_61.html"),
    url="http://www.downtownhydeparkchicago.com/about/",
)
spider = ChiSsa61Spider()

freezer = freeze_time("2019-10-04")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 22, 11, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_61/201901221100/x/commission"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_source():
    assert parsed_items[0]["source"] == "http://www.downtownhydeparkchicago.com/about/"


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
