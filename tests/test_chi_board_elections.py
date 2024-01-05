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

freezer = freeze_time("2024-01-02")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

def test_meeting_count():
    assert len(parsed_items) == 6

def test_title():
    # Note: Although this meeting is set in 2024, it appears the agency made a typo in
    # the title. The assertion below is correct despite stating "2023".
    assert (
        parsed_items[0]["title"] == "Chicago Electoral Board Meeting - January 5, 2023"
    )
    assert (
        parsed_items[1]["title"] == "Rescheduled Regular Board Meeting - December 29, 2023"
    )


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[1]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 1, 5, 10, 0)
    assert parsed_items[1]["start"] == datetime(2023, 12, 29, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_board_elections/202401051000/x/chicago_electoral_board_meeting_january_5_2023"  # noqa
    assert parsed_items[1]["id"] == "chi_board_elections/202312291000/x/regular_board_meeting_december_29_2023"  # noqa


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[1]["status"] == PASSED


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
    assert parsed_items[1]["links"] == [
      {
        "title": "Board Meeting Public Notice - December 29, 2023.pdf",
        "href": "https://cboeprod.blob.core.usgovcloudapi.net/prod/2023-12/Board Meeting Public Notice - December 29, 2023.pdf"  # noqa
      },
      {
        "title": "Board Meeting Agenda - December 29, 2023.pdf",
        "href": "https://cboeprod.blob.core.usgovcloudapi.net/prod/2023-12/Board Meeting Agenda - December 29, 2023_0.pdf"  # noqa
      },
      {
        "title": "Board Meeting Video - December 29, 2023",
        "href": "https://youtu.be/rq_QJSaplQI"
      }
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] is COMMISSION
