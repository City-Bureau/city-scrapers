from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_southwest_home_equity_i import (
    ChiSouthwestHomeEquityISpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "chi_southwest_home_equity_i.html"),
    url="https://swhomeequity.com/agenda-%26-minutes",
)

spider = ChiSouthwestHomeEquityISpider()

freezer = freeze_time("2020-09-16")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]


freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Governing Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 2, 10, 18, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See links for details"


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_southwest_home_equity_i/202002101830/x/governing_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Southwest Home Equity Assurance office",
        "address": "5334 W 65th St Chicago, IL 60638",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://swhomeequity.com/agenda-%26-minutes"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": (
                "https://img1.wsimg.com/blobby/go/ddf32f03-d1ca-4da2-ba70-a82cbae10fd5/downloads/Agenda-February%2010%2C%202020.pdf?ver=1603901723085"
            ),
            "title": "Agenda",
        },
        {
            "href": (
                "https://img1.wsimg.com/blobby/go/ddf32f03-d1ca-4da2-ba70-a82cbae10fd5/downloads/Minutes%20-%20Feb%2010%202020%20.pdf?ver=1603901723085"
            ),
            "title": "Minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
