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

freezer = freeze_time("2020-12-09")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 9


def test_title():
    assert parsed_items[0]["title"] == "Riverboat/Video Gaming"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 1, 30, 9)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See source to confirm meeting time"


def test_id():
    assert (
        parsed_items[0]["id"] == "il_gaming_board/202001300900/x/riverboat_video_gaming"
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
            "href": "http://www.igb.illinois.gov/FilesBoardMeeting/20200130CombinedAgenda.pdf",  # noqa
            "title": "Open Meeting Agenda",
        },
        {
            "href": "http://www.igb.illinois.gov/FilesBoardMeeting/20200130RiverboatAudio.mp3",  # noqa
            "title": "Casino Audio",
        },
        {
            "href": "http://www.igb.illinois.gov/FilesBoardMeeting/20200130VideoAudio.mp3",  # noqa
            "title": "Video Audio",
        },
        {
            "href": "http://www.igb.illinois.gov/FilesBoardMeeting/20200130CombinedMinutes.pdf",  # noqa
            "title": "Open Meeting Minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
