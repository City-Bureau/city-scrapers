from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response

from city_scrapers.spiders.chi_animal import ChiAnimalSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_animal.html"),
    url="https://chicago.gov/city/en/depts/cacc/supp_info/public_notice.html",
)
spider = ChiAnimalSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_len():
    assert len(parsed_items) == 3


def test_start():
    assert parsed_items[0]["start"] == datetime(2017, 9, 21)


def test_end():
    assert parsed_items[0]["end"] == datetime(2017, 9, 21, 3)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Estimated 3 hour duration"


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_class(item):
    assert item["classification"] == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Advisory Board"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "address": "2741 S. Western Ave, Chicago, IL 60608",
        "name": "David R. Lee Animal Care Center",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_status(item):
    assert item["status"] == PASSED


@pytest.mark.parametrize("item", parsed_items)
def test_sources(item):
    assert (
        item["source"]
        == "https://chicago.gov/city/en/depts/cacc/supp_info/public_notice.html"
    )


@pytest.mark.parametrize("item", parsed_items)
def test_links(item):
    assert len(item["links"]) == 0
