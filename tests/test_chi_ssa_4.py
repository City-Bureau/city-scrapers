from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_4 import ChiSsa4Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_4.html"),
    url=
    "https://95thstreetba.org/events/category/board-meeting/list/?tribe_paged=1&tribe_event_display=list&tribe-bar-date=2017-10-01",
)
spider = ChiSsa4Spider()

freezer = freeze_time("2019-12-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

def test_length():
    assert len(parsed_items) == 18

def test_title():
    assert parsed_items[0]["title"] == "95th Street Business Association Meeting"
    assert parsed_items[10]["title"] == "95th Street Business Association Meeting"


def test_description():
    assert parsed_items[0][
        "description"
    ] == "All business association members are invited to attend monthly Board Meetings on the fourth Tuesday of the month at 8 am. at the Original Pancake House, 10437 South Western Avenue. These meetings are an excellent opportunity for business owners and managers to share experiences and collaborate with one another."
    assert parsed_items[10][
        "description"
        ] == "All business association members are invited to attend monthly Board Meetings on the fourth Tuesday of the month at 8 am. at the Original Pancake House, 10437 South Western Avenue. These meetings are an excellent opportunity for business owners and managers to share experiences and collaborate with one another. (Please note: there are no Board Meetings in August or December.)"


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 5, 22, 8, 0)
    assert parsed_items[10]["start"] == datetime(2020, 3, 24, 8, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2018, 5, 22, 9, 0)
    assert parsed_items[10]["end"] == datetime(2020, 3, 24, 9, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[10]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"
                           ] == "chi_ssa_4/201805220800/x/95th_street_business_association_meeting"
    assert parsed_items[10]["id"
                           ] == "chi_ssa_4/202003240800/x/95th_street_business_association_meeting"


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[10]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Original Pancake House",
        "address": "10437 S. Western Ave. Chicago, IL 60643"
    }
    assert parsed_items[10]["location"] == {
        "name": "Original Pancake House",
        "address": "10437 S. Western Ave. Chicago, IL 60643"
    }


def test_source():
    assert parsed_items[0]["source"] == test_response.url
    assert parsed_items[10]["source"] == test_response.url


def test_links():
    assert parsed_items[0]["links"] == [{
        "href": "https://95thstreetba.org/events/95th-street-business-association-meeting/",
        "title": "meeting page"
    }]
    assert parsed_items[10]["links"] == [{
        "href": "https://95thstreetba.org/events/95th-street-business-association-meeting-11/",
        "title": "meeting page"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED
    assert parsed_items[10]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
