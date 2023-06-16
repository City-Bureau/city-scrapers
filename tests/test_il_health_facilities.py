from os.path import dirname, join
from unittest.mock import patch

import pytest
import scrapy
from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_health_facilities import IlHealthFacilitiesSpider

spider = IlHealthFacilitiesSpider()

test_response = file_response(
    join(dirname(__file__), "files", "il_health_facilities.html"),
    url="https://www2.illinois.gov/sites/hfsrb/events/Pages/Board-Meetings.aspx",
)

# The crawler for il_health_facilities grabs information from some pages that are
# linked to from the original page.
# As such, we need to test the adjacent links as well

adjacent_links = [
    "https://www2.illinois.gov/sites/hfsrb/events/Pages/March-21%202023-State-Board-Meeting.aspx",  # noqa
    "https://www2.illinois.gov/sites/hfsrb/events/Pages/May-9-2023-State-Board-Meeting.aspx",  # noqa
    "https://www2.illinois.gov/sites/hfsrb/events/Pages/June-27-2023%20State%20Board%20Meeting.aspx",  # noqa
    "https://www2.illinois.gov/sites/hfsrb/events/Pages/August-15-2023-State-Board-Meeting.aspx",  # noqa
    "https://www2.illinois.gov/sites/hfsrb/events/Pages/October-3-2023-State-Board-Meeting.aspx",  # noqa
    "https://www2.illinois.gov/sites/hfsrb/events/Pages/December-5-2023%20State%20Board%20Meeting.aspx",  # noqa
]


def mock_scrapy_request(link, callback):
    with open(
        join(dirname(__file__), "files", "il_health_facilities_helper.html"), "rb"
    ) as f:
        body = f.read()

    response = scrapy.http.HtmlResponse(
        url="my HTML string", body=body, encoding="utf-8"
    )

    result = next(callback(response))
    return result


@patch("scrapy.http.Request", mock_scrapy_request)
def generate_parsed_items():
    freezer = freeze_time("2023-02-09")
    freezer.start()

    parsed_items = [item for item in spider.parse(test_response)]

    freezer.stop()
    return parsed_items


parsed_items = generate_parsed_items()


def test_num_meetings_found():
    assert len(parsed_items) == 6


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "March 21, 2023 State Board Meeting"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_start(item):
    assert item["start"].strftime("%Y_%B_%d_%I_%M_%p") == "2023_March_21_09_00_AM"


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"].strftime("%Y_%B_%d_%I_%M_%p") == "2023_March_21_04_00_PM"


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_id(item):
    assert (
        item["id"]
        == "il_health_facilities/202303210900/x/march_21_2023_state_board_meeting"
    )


@pytest.mark.parametrize("item", parsed_items)
def test_status(item):
    assert item["status"] == TENTATIVE


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "",
        "address": "2001 Rodeo Drive, Bolingbrok, Illinois",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    item[
        "source"
    ] == "https://www2.illinois.gov/sites/hfsrb/events/Pages/Board-Meetings.aspx"


@pytest.mark.parametrize("item", parsed_items)
def test_links(item):
    assert item["links"] == [
        {
            "href": "https://www2.illinois.gov/sites/hfsrb/events/Pages/Board-Meetings.aspx",  # noqa
            "title": "Board and Subcommittee Meetings",
        },
        {
            "href": "https://www2.illinois.gov/sites/hfsrb/events/Pages/Previous-Meetings.aspx",  # noqa
            "title": "Previous Meeting",
        },
        {
            "href": "https://www2.illinois.gov/sites/hfsrb/events/Pages/Public-Hearing.aspx",  # noqa
            "title": "Public Hearings",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
