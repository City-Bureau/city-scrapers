from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_1 import ChiSsa1Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_1.html"),
    url="https://loopchicago.com/about-state-street-ssa1-2015/state-street-commission/",
)
spider = ChiSsa1Spider()

freezer = freeze_time("2018-10-12")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)], key=itemgetter("start")
)

freezer.stop()


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 1, 16, 14)


def test_id():
    assert parsed_items[0]["id"] == ("chi_ssa_1/201801161400/x/state_street_commission")


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[5]["status"] == TENTATIVE
    assert parsed_items[-1]["status"] == TENTATIVE


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://loopchicago.com/assets/State-Street-Commission-Meeting-Minutes/da3d4977e1/2018-january-16-ssc-meeting-minutes.pdf",  # noqa
            "title": "Minutes",
        }
    ]
    assert parsed_items[-1]["links"] == []


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "State Street Commission"


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
    assert item["location"] == {
        "address": "190 N State St Chicago, IL 60601",
        "name": "ABC 7 Chicago",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert (
        item["source"]
        == "https://loopchicago.com/about-state-street-ssa1-2015/state-street-commission/"  # noqa
    )
