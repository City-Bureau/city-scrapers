from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_51 import ChiSsa51Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_51.html"),
    url="http://www.cbatechworks.org/",
)
spider = ChiSsa51Spider()

freezer = freeze_time("2019-07-19")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 3, 13, 12, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 3, 13, 13, 0)


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_51/201903131200/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Commission"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "address": "806 East 78th Street, Chicago IL 60619",
        "name": "QBG Foundation",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == "http://www.cbatechworks.org/"


@pytest.mark.parametrize("item", parsed_items)
def test_links(item):
    assert item["links"] == []


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
