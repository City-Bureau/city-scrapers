from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_lsc_advisory import ChiLscAdvisorySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_lsc_advisory.html"),
    url="https://cps.edu/lscrelations/Pages/LSCAB.aspx",
)
spider = ChiLscAdvisorySpider()

freezer = freeze_time("2019-12-10")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 11


def test_title():
    assert parsed_items[0]["title"] == "Orientation"
    assert parsed_items[1]["title"] == "Advisory Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 9, 16, 18, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_lsc_advisory/201909161800/x/orientation"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == test_response.url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://cps.edu/About_CPS/Departments/Documents/LSC/LSCAB-Meeting-091619-orientation.pdf",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


def test_all_day():
    assert parsed_items[0]["all_day"] is False
