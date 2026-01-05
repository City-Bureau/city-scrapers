from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_20 import ChiSsa20Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_20.html"),
    url="https://www.mpbhba.org/business-resources/",
)
spider = ChiSsa20Spider()

freezer = freeze_time("2020-12-05")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    expected_starts = [datetime(2019, 6, 5, 9, 0), datetime(2019, 7, 10, 9, 0)]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["start"] == expected_starts[i]


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    meeting_ids = [
        "chi_ssa_20/201906050900/x/commission",
        "chi_ssa_20/201907100900/x/commission",
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["id"] == meeting_ids[i]


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Beverly Bank & Trust",
        "address": "10258 S Western Ave, Chicago, IL 60643",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.mpbhba.org/business-resources/"


def test_links():
    assert parsed_items[0]["links"] == [{"href": "", "title": ""}]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
