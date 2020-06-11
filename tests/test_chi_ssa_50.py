from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_50 import ChiSsa50Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_50.html"),
    url="http://southeastchgochamber.org/special-service-area-50/",
)
spider = ChiSsa50Spider()

freezer = freeze_time("2019-10-27")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

expected = {
    "title": COMMISSION,
    "description": "",
    "classification": COMMISSION,
    "start": "2019-04-17 00:00:00",
    "end": None,
    "all_day": False,
    "time_notes": "",
    "location": {
        "address": "8334 S Stony Island Ave, Chicago, IL 60617",
        "name": "Southeast Chicago Chamber",
    },
    "links": [],
    "source": "http://southeastchgochamber.org/special-service-area-50/",
    "status": "passed",
    "id": "chi_ssa_50/201904170000/x/commission",
}


def test_title():
    assert parsed_items[0]["title"] == expected["title"]


def test_description():
    assert parsed_items[0]["description"] == expected["description"]


def test_start():
    expected_date = expected["start"].split()[0]
    assert parsed_items[0]["start"] == datetime.strptime(expected_date, "%Y-%m-%d")


def test_end():
    assert parsed_items[0]["end"] == expected["end"]


def test_time_notes():
    assert parsed_items[0]["time_notes"] == expected["time_notes"]


def test_id():
    assert parsed_items[0]["id"] == expected["id"]


def test_status():
    assert parsed_items[0]["status"] == expected["status"]


def test_location():
    assert parsed_items[0]["location"] == expected["location"]


def test_source():
    assert parsed_items[0]["source"] == expected["source"]


def test_links():
    assert parsed_items[0]["links"] == expected["links"]


def test_classification():
    assert parsed_items[0]["classification"] == expected["classification"]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
