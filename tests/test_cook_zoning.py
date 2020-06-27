from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import FORUM, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_zoning import CookZoningSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_zoning.html"),
    url="https://www.cookcountyil.gov/agency/zoning-board-appeals-0",
)
spider = CookZoningSpider()

freezer = freeze_time("2019-07-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 12


def test_title():
    assert parsed_items[0]["title"] == "Public Hearing"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 9, 13)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "cook_zoning/201901091300/x/public_hearing"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.cookcountyil.gov/agency/zoning-board-appeals-0"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://www.cookcountyil.gov/sites/default/files/zba-agenda_1.9.19.pdf",  # noqa
        }
    ]
    assert parsed_items[-1]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == FORUM


def test_all_day():
    assert parsed_items[0]["all_day"] is False
