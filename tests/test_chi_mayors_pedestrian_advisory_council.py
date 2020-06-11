import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_mayors_pedestrian_advisory_council import (
    ChiMayorsPedestrianAdvisoryCouncilSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "chi_mayors_pedestrian_advisory_council.html"),
    url=(
        "http://chicagocompletestreets.org/getinvolved/mayors-advisory-councils/mpac-meeting-archives/"  # noqa
    ),
)
spider = ChiMayorsPedestrianAdvisoryCouncilSpider()

freezer = freeze_time("2019-06-07")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 8


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Mayor's Pedestrian Advisory Council"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime.datetime(2019, 2, 20, 15, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_mayors_pedestrian_advisory_council/201902201500/x/mayor_s_pedestrian_advisory_council"  # noqa
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

    if item["start"].date() == datetime.date(2018, 11, 7):
        doc_types = ["Meeting Minutes", "Presentations"]
    elif item["start"] > datetime.datetime(2019, 5, 1):
        doc_types = []

    assert [d["title"] for d in item["links"]] == doc_types


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == ADVISORY_COMMITTEE
