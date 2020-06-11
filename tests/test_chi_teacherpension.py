from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.http import Request, XmlResponse

from city_scrapers.spiders.chi_teacherpension import ChiTeacherPensionSpider

freezer = freeze_time("2019-04-08")
freezer.start()

test_response = file_response(
    join(dirname(__file__), "files", "chi_teacherpension.html"),
    url="https://www.ctpf.org/board-trustees-meeting-minutes",
)

with open(join(dirname(__file__), "files", "chi_teacherpension.xml"), "r") as f:
    file_content = f.read()

feed_url = "https://www.boarddocs.com/il/ctpf/board.nsf/XML-ActiveMeetings"
test_feed_response = XmlResponse(
    url=feed_url, request=Request(url=feed_url), body=str.encode(file_content)
)
spider = ChiTeacherPensionSpider()
spider._parse_minutes(test_response)
parsed_items = [item for item in spider._parse_boarddocs(test_feed_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Investment Committee"
    assert parsed_items[1]["title"] == "Board of Trustees"


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 10, 25)
    assert parsed_items[1]["start"] == datetime(2018, 10, 18, 9, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_teacherpension/201810250000/x/investment_committee"
    )


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[1]["classification"] == BOARD


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Agenda",
            "href": "http://www.boarddocs.com/il/ctpf/Board.nsf/goto?open&id=B55S995DF24B",  # noqa
        }
    ]
    assert parsed_items[20]["links"] == [
        {
            "title": "Agenda",
            "href": "http://www.boarddocs.com/il/ctpf/Board.nsf/goto?open&id=B9ATEK5665BC",  # noqa
        },
        {
            "href": "https://www.ctpf.org/sites/main/files/file-attachments/2019_february_2.pdf",  # noqa
            "title": "Minutes",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://www.boarddocs.com/il/ctpf/Board.nsf/goto?open&id=B55S995DF24B"
    )
