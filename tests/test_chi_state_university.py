import pytest

from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_state_university import ChiStateUniversitySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_state_university.html"),
    url="https://www.csu.edu/boardoftrustees/dates.htm",
)
spider = ChiStateUniversitySpider()

freezer = freeze_time("2020-09-15")
freezer.start()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()

expected = {
    "title": "Special Board Meeting",
    "classification": "Board",
    "start": datetime(2020,7,27,15,0),
    "end": None,
    "all_day": False,
    "time_notes": "",
    "location": {
        "address": "9501 S. King Drive Chicago, IL 60628",
        "name": "Room 15, 4th Floor, Gwendolyn Brooks Library Auditorium",
    },
    "links": [{
        "href": "https://attendee.gotowebinar.com/register/1203282843839078926",
        "title": "Virtual meeting link"
    }],
    "source": "https://www.csu.edu/boardoftrustees/dates.htm",
    "status": "passed",
    "id": "chi_state_university/202007271500/x/special_board_meeting",
    "description": "Monday, July 27, 2020 @ 3:00 p.m. DUE TO THE COVID-19 PANDEMIC, The July 27, 2020 SPECIAL BOARD MEETING WILL BE HELD VIA GoToWebinar - Please register here"
}


def test_items():
    assert len(parsed_items) == 12

def test_title():
    assert parsed_items[0]["title"] == expected["title"]


def test_description():
    assert parsed_items[0]["description"] == expected["description"]


def test_start():
    assert parsed_items[0]["start"] == expected["start"]



def test_end():
    assert parsed_items[0]["end"] == expected["end"]


def test_time_notes():
    assert parsed_items[0]["time_notes"] == expected["time_notes"]


def test_id():
    assert parsed_items[0]["id"] == expected["id"]


def test_status():
    assert parsed_items[0]["status"] == expected["status"]


def test_location():
    assert parsed_items[0]["location"] == expected["location"]


def test_source():
    assert parsed_items[0]["source"] == expected["source"]


def test_links():
    assert parsed_items[0]["links"] == expected["links"]


def test_classification():
    assert parsed_items[0]["classification"] == expected["classification"]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
