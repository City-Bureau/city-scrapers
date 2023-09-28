from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_citycouncil import ChiCitycouncilSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_citycouncil.json"),
    url="https://api.chicityclerkelms.chicago.gov/meeting",
)
spider = ChiCitycouncilSpider()

freezer = freeze_time("2023-09-23")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Committee on Zoning, Landmarks and Building Standards"
    )


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2023, 10, 12, 15, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert (
        parsed_items[0]["time_notes"]
        == "Please double check the meeting time on the meeting page."
    )


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_citycouncil/202310121500/x/committee_on_zoning_landmarks_and_building_standards"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Council Chamber, 2nd Floor",
        "address": "City Hall, 121 N LaSalle St - Chicago, IL 60602",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "https://api.chicityclerkelms.chicago.gov/meeting"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://chicityclerkelms.chicago.gov/Meeting/?meetingId=05889499-4C56-EE11-BE6E-001DD8098532",  # noqa
            "title": "Meeting Page",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
