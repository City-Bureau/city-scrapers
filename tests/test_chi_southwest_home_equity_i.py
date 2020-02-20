from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_southwest_home_equity_i import ChiSouthwestHomeEquityISpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_southwest_home_equity_i.html"),
    url="https://swhomeequity.com/agenda-%26-minutes",
)

spider = ChiSouthwestHomeEquityISpider()

freezer = freeze_time("2020-01-23")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]


freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 4, 8, 6, 30)


def test_end():
    assert parsed_items[0]["end"] == None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Chairman Nice began the April 8th board meeting at 6:37 pm."


def test_id():
    assert parsed_items[0]["id"] == "chi_southwest_home_equity_i/201904081830/x/board_meeting"

def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Southwest Home Equity Assurance office",
        "address": "5334 W. 65th Street in Chicago, Illinois"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://swhomeequity.com/agenda-%26-minutes"


def test_links():
    assert parsed_items[0]["links"] == [{
      "href": "https://img1.wsimg.com/blobby/go/ddf32f03-d1ca-4da2-ba70-a82cbae10fd5/downloads/Minutes%20from%20April%208%202019.pdf?ver=1581453329487",
      "title": "Minutes from April 8 2019"
    },{
      "href": "https://img1.wsimg.com/blobby/go/ddf32f03-d1ca-4da2-ba70-a82cbae10fd5/downloads/Agenda-April%208%2C%202019.pdf?ver=1581453329487",
      "title": "Agenda for April 8, 2019 (pdf)Download"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
