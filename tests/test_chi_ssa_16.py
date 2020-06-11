from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_16 import ChiSsa16Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_16.html"),
    url="https://greektownchicago.org/about/ssa-16/",
)

spider = ChiSsa16Spider()

freezer = freeze_time("2020-02-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_num():
    assert len(parsed_items) == 51


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Tax Commission"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 1, 23, 14, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    str0 = "chi_ssa_16/202001231400/x/tax_commission"
    assert parsed_items[0]["id"] == str0
    str1 = "chi_ssa_16/202002271400/x/tax_commission"
    assert parsed_items[1]["id"] == str1


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[1]["status"] == TENTATIVE
    assert parsed_items[-1]["status"] == PASSED


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "SSA #16 Office",
        "address": "306 S. Halsted St, 2nd Floor, Chicago, IL 60661",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == "https://greektownchicago.org/about/ssa-16/"


def test_links():
    assert parsed_items[0]["links"] == []

    href11 = (
        "https://5taz8eljj63owlf43qy49n1e-wpengine.netdna-ssl.com"
        "/wp-content/uploads/2019/06/SSA-16-January-24-2019-Meeting-Minutes.pdf"
    )
    assert parsed_items[11]["links"] == [{"href": href11, "title": "Minutes"}]

    href12 = (
        "https://5taz8eljj63owlf43qy49n1e-wpengine.netdna-ssl.com"
        "/wp-content/uploads/2019/06/SSA-16-February-28-2019-Meeting-Minutes.pdf"
    )
    assert parsed_items[12]["links"] == [{"href": href12, "title": "Minutes"}]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
