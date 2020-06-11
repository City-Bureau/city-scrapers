from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_board_elections import ChiBoardElectionsSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_board_elections.html"),
    url="https://app.chicagoelections.com/pages/en/board-meetings.aspx",
)
spider = ChiBoardElectionsSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2018-11-30")
freezer.start()

parsed_items = [item for item in spider._next_meeting(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Electoral Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 11, 27, 9, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_board_elections/201811270930/x/electoral_board"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "8th Floor Office, 69 W. Washington St. Chicago, IL 60602",
        "name": "Cook County Administration Building",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://app.chicagoelections.com/pages/en/board-meetings.aspx"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://app.chicagoelections.com/documents/general/Standard-Board-Meeting-Agenda.pdf?date=20181127",  # noqa
        }
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] is COMMISSION


# Previous meetings on different page
prev_url = "https://app.chicagoelections.com/pages/en/meeting-minutes-and-videos.aspx"
test_response_prev = file_response(
    join(dirname(__file__), "files", "chi_board_elections_prev.html"), url=prev_url
)

freezer.start()

parsed_items_prev = [item for item in spider._prev_meetings(test_response_prev)]

freezer.stop()


def test_count():
    assert len(parsed_items_prev) == 12


def test_title_prev():
    assert parsed_items_prev[0]["title"] == "Electoral Board"


def test_description_prev():
    assert parsed_items_prev[0]["description"] == ""


def test_start_prev():
    assert parsed_items_prev[0]["start"] == datetime(2018, 11, 27, 9, 30)


def test_end_prev():
    assert parsed_items_prev[0]["end"] is None


def test_id_prev():
    assert (
        parsed_items_prev[0]["id"]
        == "chi_board_elections/201811270930/x/electoral_board"
    )


def test_status_prev():
    assert parsed_items_prev[0]["status"] == PASSED


def test_location_prev():
    assert parsed_items_prev[0]["location"] == {
        "address": "8th Floor Office, 69 W. Washington St. Chicago, IL 60602",
        "name": "Cook County Administration Building",
    }


def test_source_prev():
    assert (
        parsed_items_prev[0]["source"]
        == "https://app.chicagoelections.com/pages/en/meeting-minutes-and-videos.aspx"
    )


def test_links_prev():
    assert parsed_items_prev[4]["links"] == [
        {
            "title": "Minutes",
            "href": "https://app.chicagoelections.com/documents/general/BoardMeetingMinutes-2018-10-30.pdf",  # noqa
        },
        {"title": "Video", "href": "https://youtu.be/AKFNigWEkc0"},
    ]


@pytest.mark.parametrize("item", parsed_items_prev)
def test_all_day_prev(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items_prev)
def test_classification_prev(item):
    assert item["classification"] == COMMISSION
