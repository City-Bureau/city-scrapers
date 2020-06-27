import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response

from city_scrapers.spiders.chi_mayors_bicycle_advisory_council import (
    ChiMayorsBicycleAdvisoryCouncilSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "chi_mayors_bicycle_advisory_council.html"),
)
spider = ChiMayorsBicycleAdvisoryCouncilSpider()
parsed_items = [item for item in spider.parse(test_response)]


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Mayor's Bicycle Advisory Council"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime.datetime(2018, 3, 7, 15, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_mayors_bicycle_advisory_council/201803071500/x/mayor_s_bicycle_advisory_council"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "address": "121 N LaSalle St, Chicago, IL 60602",
        "name": "City Hall, Room 1103",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == spider.BASE_URL


@pytest.mark.parametrize("item", parsed_items)
def test_links(item):
    doc_types = ["Agenda", "Meeting Minutes", "Presentations"]

    if item["start"] == datetime.datetime(2015, 6, 11, 15):
        doc_types.append("D. Taylor Comments")
    elif item["start"] == datetime.datetime(2015, 3, 12, 15):
        doc_types.remove("Presentations")
    elif item["start"] == datetime.datetime(2018, 12, 12, 15):
        doc_types = []

    assert [d["title"] for d in item["links"]] == doc_types


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == ADVISORY_COMMITTEE
