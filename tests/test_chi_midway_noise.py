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

def test_start():
    expected_starts = [datetime(2013, 1, 24, 18, 30),
                       datetime(2013, 2, 28, 18, 30),
                       datetime(2013, 4, 2, 18, 30),
                       datetime(2013, 4, 25, 18, 30),
                       datetime(2013, 7, 25, 18, 30),
                       datetime(2013, 10, 22, 18, 30),
                       datetime(2013, 10, 24, 18, 30),
                       datetime(2014, 1, 23, 18, 30),
                       datetime(2014, 4, 24, 18, 30),
                       datetime(2014, 7, 24, 18, 30),
                       datetime(2014, 10, 23, 18, 30),
                       datetime(2015, 1, 22, 18, 30),
                       datetime(2015, 4, 23, 18, 30),
                       datetime(2015, 7, 23, 18, 30),
                       datetime(2015, 10, 22, 18, 30),
                       datetime(2016, 1, 28, 18, 30),
                       datetime(2016, 4, 28, 18, 30),
                       datetime(2016, 7, 26, 18, 30),
                       datetime(2016, 7, 28, 18, 30),
                       datetime(2016, 10, 27, 18, 30),
                       datetime(2017, 1, 23, 18, 30),
                       datetime(2017, 1, 26, 18, 30),
                       datetime(2017, 4, 27, 18, 30),
                       datetime(2017, 7, 27, 18, 30),
                       datetime(2017, 10, 26, 18, 30),
                       datetime(2018, 1, 25, 18, 30),
                       datetime(2018, 1, 30, 18, 30),
                       datetime(2018, 4, 26, 18, 30),
                       datetime(2018, 7, 26, 18, 30),
                       datetime(2018, 10, 25, 18, 30),
                       datetime(2019, 1, 24, 18, 30),
                       datetime(2019, 4, 25, 18, 30),
                       datetime(2019, 7, 25, 18, 30),
                       datetime(2019, 10, 24, 18, 30),
                       ]

    for i in range(len(parsed_items)):
        assert parsed_items[i]["start"] == expected_starts[i]


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
