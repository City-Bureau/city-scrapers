from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_elections import IlElectionsSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_elections.html"),
    url="https://www.elections.il.gov/AboutTheBoard/Agenda.aspx",
)
spider = IlElectionsSpider()

freezer = freeze_time("2019-12-04")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Illinois State Board of Elections"


def test_description():
    assert parsed_items[0]["description"
                           ] == "Statutory meeting for election of Chairman and Vice Chairman."


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 7, 1, 10, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "il_elections/201907011030/x/illinois_state_board_of_elections"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {"name": "Springfield", "address": ""}


def test_source():
    assert parsed_items[0]["source"] == "https://www.elections.il.gov/AboutTheBoard/Agenda.aspx"


def test_links():
    assert parsed_items[0]["links"] == [{
        "href":
            "https://www.elections.il.gov/DocDisplay.aspx?Doc=/Downloads/AboutTheBoard/PDF/07_01_19Agenda.pdf",
        "title": ""
    }]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
