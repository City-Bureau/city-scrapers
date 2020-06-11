from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CANCELLED, COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_17 import ChiSsa17Spider

freezer = freeze_time("2019-03-17")
freezer.start()
spider = ChiSsa17Spider()
res = file_response(join(dirname(__file__), "files", "chi_ssa_17.html"))
parsed_items = [item for item in spider.parse(res)]
freezer.stop()


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 30, 10)


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_17/201901301000/x/ssa_17_commission"


def test_status():
    assert parsed_items[0]["status"] == CANCELLED
    assert parsed_items[-1]["status"] == TENTATIVE


def test_links():
    assert parsed_items[0]["links"] == []


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "SSA #17 Commission"


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
    spider = ChiSsa17Spider()
    assert item["location"] == spider.location


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
