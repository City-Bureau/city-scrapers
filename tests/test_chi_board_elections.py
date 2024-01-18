from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_board_elections import ChiBoardElectionsSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_board_elections.html"),
    url="https://chicagoelections.gov/about-board/board-meetings",
)
spider = ChiBoardElectionsSpider()

freezer = freeze_time("2024-01-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_meeting_count():
    assert len(parsed_items) == 7


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Rescheduled Regular Board Meeting - January 12, 2024"
    )
    assert (
        parsed_items[1]["title"] == "Chicago Electoral Board Meeting - January 12, 2024"
    )


def test_description():
    assert (
        parsed_items[0]["description"]
        == "The next Regular Board meeting of the Board of Election Commissioners has been rescheduled to Friday, January 12, 2024 at 10:00 a.m."  # noqa
    )
    assert (
        parsed_items[1]["description"]
        == "The next Chicago Electoral Board Meeting will be held on Friday, January 12, 2024 at 10:30am."  # noqa
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 1, 12, 10, 0)
    assert parsed_items[1]["start"] == datetime(2024, 1, 12, 10, 30)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_board_elections/202401121000/x/regular_board_meeting_january_12_2024"  # noqa
    )
    assert (
        parsed_items[1]["id"]
        == "chi_board_elections/202401121030/x/chicago_electoral_board_meeting_january_12_2024"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    # Item 2 is the first item in the list that has a status of PASSED
    assert parsed_items[2]["status"] == PASSED


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
            "title": "Board Meeting Public Notice - January 12, 2024.pdf",
            "href": "https://cboeprod.blob.core.usgovcloudapi.net/prod/2024-01/Board Meeting Public Notice - January 12, 2024_0.pdf",  # noqa
        },
        {
            "title": "Board Meeting Agenda - January 12, 2024.pdf",
            "href": "https://cboeprod.blob.core.usgovcloudapi.net/prod/2024-01/Board Meeting Agenda - January 12, 2024_0.pdf",  # noqa
        },
        {
            "title": "Board Meeting Video - January 12, 2024",
            "href": "https://www.youtube.com/watch?v=x9HJVhbxTPw",  # noqa
        },
    ]
    assert parsed_items[1]["links"] == [
        {
            "title": "Electoral Board Meeting Notice - January 12, 2024.pdf",
            "href": "https://cboeprod.blob.core.usgovcloudapi.net/prod/2024-01/Electoral Board Meeting Notice - January 12, 2024.pdf",  # noqa
        },
        {
            "title": "Electoral Board Meeting Agenda - January 12, 2024 Revised.pdf",
            "href": "https://cboeprod.blob.core.usgovcloudapi.net/prod/2024-01/Electoral Board Meeting Agenda - January 12, 2024 Revised.pdf",  # noqa
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] is COMMISSION
