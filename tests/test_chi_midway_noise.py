from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_midway_noise import ChiMidwayNoiseSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_midway_noise.html"),
    url="https://www.flychicago.com",
)
spider = ChiMidwayNoiseSpider()

freezer = freeze_time("2019-09-22")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 34


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Midway Noise Compatibility Commission Meeting"


# def test_description():
#     assert parsed_items[0]["description"] == "EXPECTED DESCRIPTION"

# def test_start():
#     assert parsed_items[0]["start"] == datetime(2019, 1, 1, 0, 0)

@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == "No start times given; past records indicate 6:30PM."

# def test_id():
#     assert parsed_items[0]["id"] == "EXPECTED ID"


def test_status():
    expected_statuses = [PASSED for i in range(33)]
    expected_statuses.append(TENTATIVE)
    for j in range(len(parsed_items)):
        assert parsed_items[j]["status"] == expected_statuses[j]


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "The Mayfield",
        "address": "6072 S. Archer Ave., Chicago, IL 60638"
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == "https://www.flychicago.com/community/MDWnoise/AdditionalResources/pages/default.aspx"

# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
