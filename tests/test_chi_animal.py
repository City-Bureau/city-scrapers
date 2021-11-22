from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import ADVISORY_COMMITTEE, CANCELLED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_animal import ChiAnimalSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_animal.html"),
    url="https://chicago.gov/city/en/depts/cacc/supp_info/public_notice.html",
)
spider = ChiAnimalSpider()


freezer = freeze_time("2020-01-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_len():
    assert len(parsed_items) == 5


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 3, 19, 8, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2020, 3, 19, 11, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Estimated 3 hour duration"


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


def test_title():
    assert parsed_items[0]["title"] == "Advisory Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "2741 S. Western Ave, Chicago, IL 60608",
        "name": "David R. Lee Animal Care Center",
    }


def test_status():
    assert parsed_items[0]["status"] == CANCELLED


def test_source():
    assert parsed_items[0]["source"] == test_response.url


def test_links():
    assert parsed_items[2]["links"] == [
        {
            "href": "https://vimeo.com/449924512",
            "title": "Recorded video link to the meeting held on August 20th",
        }
    ]
