from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_gaming_board import IlGamingBoardSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_gaming_board.html"),
    url="http://www.igb.illinois.gov/MeetingsMinutes.aspx",
)
spider = IlGamingBoardSpider()

freezer = freeze_time("2019-06-04")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 10


def test_title():
    assert parsed_items[0]["title"] == "Riverboat/Video Gaming"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 30, 9)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See source to confirm meeting time"


def test_id():
    assert (
        parsed_items[0]["id"] == "il_gaming_board/201901300900/x/riverboat_video_gaming"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"] == "http://www.igb.illinois.gov/MeetingsMinutes.aspx"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://www.igb.illinois.gov/FilesBoardMeeting/20190130RiverboatAgenda.pdf",  # noqa
            "title": "Agenda: Riverboat",
        },
        {
            "href": "http://www.igb.illinois.gov/FilesBoardMeeting/20190130RiverboatMinutes.pdf",  # noqa
            "title": "Minutes: Riverboat",
        },
        {
            "href": "http://www.igb.illinois.gov/FilesBoardMeeting/20190130RiverboatAudio.mp3",  # noqa
            "title": "Audio: Riverboat",
        },
        {
            "href": "http://www.igb.illinois.gov/FilesBoardMeeting/20190130VideoAudio.mp3",  # noqa
            "title": "Audio: Video Gaming",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
