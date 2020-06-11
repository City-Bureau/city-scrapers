from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_2 import ChiSsa2Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_2.html"),
    url="http://belmontcentral.org/about-ssa-2/ssa2-meeting-minutes-audit/",
)
spider = ChiSsa2Spider()

freezer = freeze_time("2019-07-18")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 10, 2, 14, 0)


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_2/201810021400/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://belmontcentral.org/wp-content/uploads/2018/12/October-2-2018-SSA-Minutes.pdf",  # noqa
            "title": "Minutes",
        }
    ]


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
def test_end(item):
    assert item["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == spider.location


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert (
        item["source"]
        == "http://belmontcentral.org/about-ssa-2/ssa2-meeting-minutes-audit/"
    )


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
