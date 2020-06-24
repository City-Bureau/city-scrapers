from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_38 import ChiSsa38Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_38.html"),
    url="http://www.northcenterchamber.com/pages/MeetingsTransparency1",
)
spider = ChiSsa38Spider()

freezer = freeze_time("2020-06-20")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


# def test_tests():
#     print("Please write some tests for this spider or at least disable this one.")
#     assert False


"""
Uncomment below
"""
@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Chamber of Commerce"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 2, 28, 10, 0)
    assert parsed_items[1]["start"] == datetime(2020, 5, 1, 10, 0)
    assert parsed_items[2]["start"] == datetime(2020, 7, 13, 10, 0)


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] == None


# def test_time_notes():
#     assert parsed_items[0]["time_notes"] == "EXPECTED TIME NOTES"


# def test_id():
#     assert parsed_items[0]["id"] == "EXPECTED ID"


# def test_status():
#     assert parsed_items[0]["status"] == "EXPECTED STATUS"


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "Northcenter Chamber of Commerce",
        "address": "4054 N Lincoln Ave, Chicago, IL 60618"
    }


# def test_source():
#     assert parsed_items[0]["source"] == "EXPECTED URL"


# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]


# def test_classification():
#     assert parsed_items[0]["classification"] == NOT_CLASSIFIED


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
