from datetime import datetime  # noqa
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CANCELLED, NOT_CLASSIFIED, TENTATIVE
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


# def test_start():
#    assert parsed_items[0]["start"] == datetime(2023, 10, 12, 12, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert (
        parsed_items[0]["time_notes"]
        == "Please double check the meeting time on the meeting notice and/or agenda."
    )


# def test_id():
#    assert (
#        parsed_items[0]["id"]
#        == "chi_citycouncil/202310121500/x/committee_on_zoning_landmarks_and_building_standards"  # noqa
#    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_status_cancelled():
    assert parsed_items[1]["status"] == CANCELLED
    assert parsed_items[6]["status"] == CANCELLED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Council Chamber, 2nd Fl, City Hall",
        "address": "121 N LaSalle St - Chicago, IL 60602",
    }


def test_location_committee_room():
    assert parsed_items[26]["location"] == {
        "name": "Room 201A, 2nd Fl, City Hall",
        "address": "121 N. LaSalle St - Chicago, IL 60602",
    }


def test_location_bare_room_number():
    item = {"location": "201A, 2nd Floor, City Hall, 121 North LaSalle Street"}
    assert spider._parse_location(item) == {
        "name": "Room 201A, 2nd Floor, City Hall",
        "address": "121 North LaSalle Street",
    }


def test_location_offsite():
    assert parsed_items[71]["location"] == {
        "name": "Credit Union 1 Arena (UIC Pavilion)",
        "address": "525 S Racine Ave, Chicago, IL 60607",
    }


def test_location_without_street_address():
    assert parsed_items[72]["location"] == spider.default_location


def test_source():
    assert parsed_items[0]["source"] == "https://chicityclerkelms.chicago.gov/Meetings/"


# def test_links():
#    assert parsed_items[0]["links"] == [
#        {
#            "href": "https://occprodstoragev1.blob.core.usgovcloudapi.net/meetingattachmentspublic/12872b2c-96aa-497a-961a-2929d592b6ca.pdf",  # noqa
#            "title": "Notice",
#        }
#    ]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
