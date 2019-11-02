import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
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

with open(join(dirname(__file__), "files",
               "chi_ssa_50.json")) as expected_file:
    expected = json.load(expected_file)


def test_title():
    assert parsed_items[0]["title"] == expected[0]["title"]


def test_description():
    assert parsed_items[0]["description"] == expected[0]["description"]


def test_start():
    expected_date = expected[0]["start"].split()[0]
    assert parsed_items[0]["start"] == datetime.strptime(
        expected_date, "%Y-%m-%d")


def test_end():
    expected_date = expected[0]["end"].split()[0]
    assert parsed_items[0]["end"] == datetime.strptime(expected_date,
                                                       "%Y-%m-%d")


def test_time_notes():
    assert parsed_items[0]["time_notes"] == expected[0]["time_notes"]


def test_id():
    assert parsed_items[0]["id"] == expected[0]["id"]


def test_status():
    assert parsed_items[0]["status"] == expected[0]["status"]


def test_location():
    assert parsed_items[0]["location"] == expected[0]["location"]


def test_source():
    assert parsed_items[0]["source"] == expected[0]["source"]


def test_links():
    assert parsed_items[0]["links"] == expected[0]["links"]


def test_classification():
    assert parsed_items[0]["classification"] == expected[0]["classification"]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
