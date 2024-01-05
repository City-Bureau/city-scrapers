from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_board_elections import ChiBoardElectionsSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_board_elections.html"),
    url="https://chicagoelections.gov/about-board/board-meetings",
)
spider = ChiBoardElectionsSpider()

freezer = freeze_time("2018-11-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"] == "Chicago Electoral Board Meeting - January 5, 2023"
    )


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 1, 5, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_board_elections/202401051000/x/chicago_electoral_board_meeting_january_5_2023"  # noqa


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Board's Conference Room",
        "address": "Suite 800, 69 West Washington Street, Chicago, Illinois",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://chicagoelections.gov/about-board/board-meetings"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Electoral Board Meeting Notice - January 5, 2024.pdf",
            "href": "https://cboeprod.blob.core.usgovcloudapi.net/prod/2024-01/Electoral Board Meeting Notice - January 5, 2024_0.pdf",  # noqa
        },
        {
            "title": "Electoral Board Meeting Agenda - January 5, 2024.pdf",
            "href": "https://cboeprod.blob.core.usgovcloudapi.net/prod/2024-01/Electoral Board Meeting Agenda - January 5, 2024_0.pdf",  # noqa
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] is COMMISSION
