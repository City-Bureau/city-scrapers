from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wayne_state_university import WayneStateUniversitySpider

test_response = file_response(
    join(dirname(__file__), "files", "wayne_state_university.html"),
    url="http://bog.wayne.edu/",
)
spider = WayneStateUniversitySpider()

freezer = freeze_time("2019-10-08")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board standing committee meetings"

def test_meeting_collection():
    assert parsed_items[0]["meetings"] == " "

def test_description():
    assert parsed_items[0]["description"] == ""

def test_start():
    assert parsed_items[0]["start"] == "December 6, 2019 at 9:00 a.m"


def test_end():
    assert parsed_items[0]["end"] == "Ending Time Not Specified"


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See source to confirm details. Times may change"


def test_id():
    assert parsed_items[0]["id"] == "EXPECTED ID"


def test_status():
    assert parsed_items[0]["status"] == "EXPECTED STATUS"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "McGregor Memorial Conference Center",
        "address": "495 Gilmour Mall, Detroit, MI 48202",
    }


def test_source():
    assert parsed_items[0]["source"] == "http://bog.wayne.edu/"


def test_links():
    assert parsed_items[0]["links"] == [{
       "href": "/meetings/2019/09-20",
       "title": "December 6, 2019 Meeting"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
