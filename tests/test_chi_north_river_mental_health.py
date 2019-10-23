from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_north_river_mental_health import ChiNorthRiverMentalHealthSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_north_river_mental_health.html"),
    url="http://www.northriverexpandedmentalhealthservicescommission.org/index.html",
)
spider = ChiNorthRiverMentalHealthSpider()

freezer = freeze_time("2019-10-10")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Governing Commission"


def test_description():
    assert parsed_items[0]["description"] == ''


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 1, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ''


# def test_id():
#     assert parsed_items[0]["id"] == "EXPECTED ID"


# def test_status():
#     assert parsed_items[0]["status"] == "EXPECTED STATUS"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "North River Expanded Mental Health Services Program Governing Commission Office",
        "address": "3525 W. Peterson Ave, Unit 306, Chicago, IL 60659"
    }


def test_source():
    assert parsed_items[0]["source"] == "http://www.northriverexpandedmentalhealthservicescommission.org/index.html"


# def test_links():
#     assert parsed_items[0]["links"] == [{
#        "href": "EXPECTED HREF",
#        "title": "EXPECTED TITLE"
#     }]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
