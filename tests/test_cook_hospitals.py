from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.cook_hospitals import CookHospitalsSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_hospitals.html"),
    url=(
        "https://cookcountyhealth.org/about/board-of-directors/board-committee-meetings-agendas-minutes/"  # noqa
    ),
)
spider = CookHospitalsSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2019-10-15")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 37


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 4, 26, 9, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Confirm time in agenda"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://cookcountyhealth.org/wp-content/uploads/04-26-19-Board-Agenda-1.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://cookcountyhealth.org/wp-content/uploads/Committee-Metrics-combined-04-26-19-1.pdf",  # noqa
            "title": "Committee Metrics",
        },
        {
            "href": "https://cookcountyhealth.org/wp-content/uploads/Item-VA-Contract-and-Procurement-Item-04-26-19-1.pdf",  # noqa
            "title": "Item V(A) Contract and Procurement Item",
        },
        {
            "href": "https://cookcountyhealth.org/wp-content/uploads/Item-VII-Report-from-the-CEO-04-26-19-1.pdf",  # noqa
            "title": "Item VII Report from the CEO",
        },
        {
            "href": "https://cookcountyhealth.org/wp-content/uploads/Item-VIIIA-SP-discussion-Marketing-04-26-19-4.pdf",  # noqa
            "title": "Item VIII(A) SP discussion Marketing",
        },
        {
            "href": "https://cookcountyhealth.org/wp-content/uploads/Item-VIIIA-SP-discussion-Marketing-04-26-19-5.pdf",  # noqa
            "title": "Item VIII(A) SP Discussion CCDPH",
        },
        {
            "href": "https://cookcountyhealth.org/wp-content/uploads/Item-VIIIB-CCDPH-2nd-Quarterly-Report-04-26-19-1.pdf",  # noqa
            "title": "Item VIII(B) Q2 Report from CCDPH",
        },
    ]


def test_id():
    assert parsed_items[0]["id"] == "cook_hospitals/201904260900/x/board_of_directors"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[-1]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert (
        item["source"]
        == "https://cookcountyhealth.org/about/board-of-directors/board-committee-meetings-agendas-minutes/"  # noqa
    )
