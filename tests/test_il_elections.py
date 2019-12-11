from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.http import HtmlResponse

from city_scrapers.spiders.il_elections import IlElectionsSpider

freezer = freeze_time("2019-12-04")
freezer.start()

test_response = file_response(
    join(dirname(__file__), "files", "il_elections_minutes.html"),
    url="https://www.elections.il.gov/AboutTheBoard/MeetingMinutesAll.aspx",
)

with open(join(dirname(__file__), "files", "il_elections_agenda.html"), "r") as f:
    file_content = f.read()

feed_url = "https://www.elections.il.gov/AboutTheBoard/Agenda.aspx"
test_feed_response = HtmlResponse(url=feed_url, body=str.encode(file_content))

spider = IlElectionsSpider()
spider._parse_minutes(test_response)
spider._parse_addresses(test_response)
parsed_items = [item for item in spider._parse_agenda(test_feed_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Illinois State Board of Elections"
    assert parsed_items[1]["title"] == "Illinois State Board of Elections"


def test_description():
    assert parsed_items[0]["description"
                           ] == "Statutory meeting for election of Chairman and Vice Chairman."
    assert parsed_items[1]["description"] == ""
    assert parsed_items[6][
        "description"] == "Statutory date to certify the ballot for the March Primary Election."


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 7, 1, 10, 30)
    assert parsed_items[1]["start"] == datetime(2019, 8, 21, 10, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "il_elections/201907011030/x/illinois_state_board_of_elections"


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[5]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Springfield",
        "address":
            "2329 S. MacArthur Blvd. Springfield, IL 62704 Phone: 217-782-4141 Fax: 217-782-5959"
    }
    assert parsed_items[5]["location"] == {
        "address":
            "100 W. Randolph, Suite 14-100 Chicago, IL 60601 Phone: 312-814-6440 Fax: 312-814-6485",
        "name": "Chicago"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.elections.il.gov/AboutTheBoard/Agenda.aspx"


def test_links():
    assert parsed_items[0]["links"] == [{
        "href":
            "https://www.elections.il.gov/DocDisplay.aspx" +
            "?Doc=/Downloads/AboutTheBoard/PDF/07_01_19Agenda.pdf",
        "title": "Agenda"
    }, {
        "href":
            "https://www.elections.il.gov/DocDisplay.aspx" +
            "?Doc=/Downloads/AboutTheBoard/PDF/July 1-19 regular meeting minutes.pdf",
        "title": "Minutes"
    }]
    assert parsed_items[7]["links"] == [{"href": "", "title": ""}]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
