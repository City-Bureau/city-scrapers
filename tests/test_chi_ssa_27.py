from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.constants import COMMITTEE

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_27 import ChiSsa27Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_27.html"),
    url="https://www.lakeviewchamber.com/ssa27",
)
spider = ChiSsa27Spider()

freezer = freeze_time("2019-07-03")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


# def test_tests():
#     print("Please write some tests for this spider or at least disable this one.")
#     assert False


"""
Uncomment below
"""

def test_title():
    assert parsed_items[0]["title"] == "EXPECTED TITLE"

def test_description():
    assert parsed_items[0]["description"] == ""

def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 1, 0, 0)

def test_end():
    assert parsed_items[0]["end"] is None

def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""

def test_id():
    assert parsed_items[0]["id"] == 'chi_ssa_27/201912120830/x/commission'

def test_status():
    assert parsed_items[0]["status"] == "tentative"

def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Sheil Park",
        "address": "3505 N. Southport Ave., Chicago, IL 60657"
    }

def test_source():
    assert parsed_items[0]["source"] == "https://www.lakeviewchamber.com/ssa27"

# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]

def test_classification():
    assert parsed_items[0]["classification"] == ( COMMISSION | COMMITTEE )

@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
