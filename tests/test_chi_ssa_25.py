from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_25 import ChiSsa25Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_25.html"),
    url="http://littlevillagechamber.org/2019-meetings-minutes/",
)
spider = ChiSsa25Spider()

freezer = freeze_time("2019-03-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Commission: Monthly"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 15, 9)
    assert parsed_items[-1]["start"] == datetime(2019, 12, 17, 9)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 1, 15, 10)
    assert parsed_items[-1]["end"] == datetime(2019, 12, 17, 10)


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_25/201901150900/x/commission_monthly"


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[-1]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "LV Chamber",
        "address": "3610 W. 26th St. 2nd Floor Chicago, IL",
    }
    assert parsed_items[-1]["location"] == {
        "name": "Nuevo Leo Restaurant",
        "address": "3657 W 26th St. 2nd Floor Chicago, IL",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://littlevillagechamber.org/2019-meetings-minutes/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://littlevillagechamber.org/wp-content/uploads/2019/03/SSA-Jan.-15.-2019-Meeting-Minutes.pdf",  # noqa
            "title": "Minutes",
        }
    ]
    assert parsed_items[-1]["links"] == []


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
