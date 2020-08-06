from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_pace_board import CookPaceBoardSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_pace_board.html"),
    url="https://www.pacebus.com/meeting/citizens-advisory-board-meeting-91719",
)
spider = CookPaceBoardSpider()


freezer = freeze_time("2020-08-06")
freezer.start()

parsed_item = [item for item in spider._parse_detail(test_response)][0]

freezer.stop()


def test_title():
    assert parsed_item["title"] == "Citizens Advisory Board"


def test_all_day():
    assert parsed_item["all_day"] is False


def test_description():
    assert parsed_item["description"] == ""


def test_start():
    assert parsed_item["start"] == datetime(2019, 9, 17, 10)


def test_end():
    assert parsed_item["end"] == datetime(2019, 9, 17, 11)


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_id():
    assert isinstance(parsed_item["id"], str) and parsed_item["id"] != ""


def test_status():
    assert parsed_item["status"] == PASSED


def test_location():
    assert parsed_item["location"] == {
        "name": "Pace Headquarters Room 132",
        "address": "550 W Algonquin Rd Arlington Heights, IL 60005",
    }


def test_source():
    assert parsed_item["source"] == test_response.url


def test_classification():
    assert parsed_item["classification"] == ADVISORY_COMMITTEE


def test_links():
    assert parsed_item["links"] == [
        {
            "href": "https://www.pacebus.com/sites/default/files/2020-06/CAB%20Minutes%209.17.19.pdf",  # noqa
            "title": "CAB Minutes 9/17/19",
        },
    ]
