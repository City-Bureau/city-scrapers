from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_25 import ChiSsa25Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_25.html"),
    url="https://littlevillagechamber.org/calendar/november-ssa-meeting-2019/",
)
spider = ChiSsa25Spider()

freezer = freeze_time("2020-08-07")
freezer.start()

parsed_item = [item for item in spider._parse_detail(test_response)][0]

freezer.stop()


def test_title():
    assert parsed_item["title"] == "November SSA Meeting 2019"


def test_start():
    assert parsed_item["start"] == datetime(2019, 11, 19, 9)


def test_end():
    assert parsed_item["end"] == datetime(2019, 11, 19, 10)


def test_id():
    assert parsed_item["id"] == "chi_ssa_25/201911190900/x/november_ssa_meeting_2019"


def test_status():
    assert parsed_item["status"] == PASSED


def test_location():
    assert parsed_item["location"] == {
        "name": "Second Federal A Division of Self-Help FCU",
        "address": "3960 w 26th st chicago, IL 60623",
    }


def test_source():
    assert parsed_item["source"] == test_response.url


def test_links():
    assert parsed_item["links"] == [
        {
            "href": "https://littlevillagechamber.org/wp-content/uploads/Nov-15-2019-SSA-25-Meeting-Minutes.pdf",  # noqa
            "title": "Minutes",
        }
    ]


def test_classification():
    assert parsed_item["classification"] == COMMISSION
