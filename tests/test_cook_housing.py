from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, FORUM, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_housing import CookHousingSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_housing.html"),
    url="http://thehacc.org/events/",
)
spider = CookHousingSpider()

freezer = freeze_time("2019-10-03")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 4


def test_title():
    assert parsed_items[0]["title"] == "Landlord Workshop – Nuts and Bolts of the HCV Program"
    assert parsed_items[1]["title"] == "Housing Authority of Cook County Board Meeting"


def test_description():
    assert parsed_items[0]["description"] == "To Register Click Here"
    assert parsed_items[1]["description"] == "Regular Board of Commissioners Meetings All " \
                                             "meetings start at 2:00 p.m., Central Time " \
                                             "HACC Central Office Board Room 175 West " \
                                             "Jackson, Suite 350, Chicago, IL"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 10, 10, 13, 0)
    assert parsed_items[1]["start"] == datetime(2019, 10, 17, 14, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 10, 10, 14, 30)
    assert parsed_items[1]["end"] == datetime(2019, 10, 17, 16, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[1]["time_notes"] == ""


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[1]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Turlington West Apts.",
        "address": "15306 S. Robey Ave."
    }
    assert parsed_items[1]["location"] == {"name": "HACC Downtown", "address": "175 W Jackson Blvd"}


def test_source():
    assert parsed_items[0]["source"] == "http://thehacc.org/events/"


def test_links():
    assert parsed_items[0]["links"] == [{
        "href": "http://thehacc.org/event/landlord-workshop-nuts-and-bolts-of-the-hcv-program-3/",
        "title": "Landlord Workshop – Nuts and Bolts of the HCV Program"
    }]
    assert parsed_items[1]["links"] == [{
        "href":
            "http://thehacc.org/event/"
            "housing-authority-of-cook-county-board-meeting-2-2-2-2-4/",
        "title": "Housing Authority of Cook County Board Meeting"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == FORUM
    assert parsed_items[1]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
