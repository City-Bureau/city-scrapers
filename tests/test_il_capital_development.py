from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_capital_development import IlCapitalDevelopmentSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_capital_development.html"),
    url="https://www2.illinois.gov/cdb/about/boardmeetings/Pages/20192020Meetings.aspx",
)
spider = IlCapitalDevelopmentSpider()

freezer = freeze_time("2019-10-26")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Capital Development Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 7, 9, 11, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 7, 10, 12, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_capital_development/201907091100/x/capital_development_board"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "James R. Thompson Center",
        "address": "100 West Randolph Street, 14th Floor, Chicago, IL 60601",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www2.illinois.gov/cdb/about/boardmeetings/Pages/20192020Meetings.aspx"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www2.illinois.gov/cdb/about/boardmeetings/Documents/2019-2020/TableOfContentsWEB-July.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www2.illinois.gov/cdb/about/boardmeetings/Documents/2019-2020/July%20Board%20Book%20-%20Public.pdf",  # noqa
            "title": "Board Book",
        },
        {
            "href": "https://www2.illinois.gov/cdb/about/boardmeetings/Documents/2019-2020/07.09.19%20Meeting%20Minutes.docx",  # noqa
            "title": "Meeting Minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
