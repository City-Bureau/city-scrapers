from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_state_university import ChiStateUniversitySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_state_university.html"),
    url="https://www.csu.edu/boardoftrustees/dates.htm",
)
spider = ChiStateUniversitySpider()

freezer = freeze_time("2019-11-29")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

expected = {
    "title": "Board of Trustees Meetings",
    "classification": "Board",
    "start": "2019-03-01 00:00:00",
    "end": None,
    "all_day": False,
    "time_notes": "Rescheduled to TBD",
    "location": {
        "address": "Room 415",
        "name": "Gwendolyn Brooks Library Auditorium"
    },
    "source": "https://www.csu.edu/boardoftrustees/dates.htm",
    "status": "cancelled",
    "id": "chi_state_university/201903010000/x/board_of_trustees_meetings"
}


def test_title():
    assert parsed_items[0]["title"] == expected["title"]


def test_start():
    expected_date = expected["start"].split()[0]
    assert parsed_items[0]["start"] == datetime.strptime(expected_date, "%Y-%m-%d")


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


def test_classification():
    assert parsed_items[0]["classification"] == expected["classification"]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
