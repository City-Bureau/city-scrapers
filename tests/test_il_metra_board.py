from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.il_metra_board import IlMetraBoardSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_metra_board.html"),
    url="https://metrarr.granicus.com/ViewPublisher.php?view_id=5",
)
spider = IlMetraBoardSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2018-01-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Metra February 2018 Board Meeting"


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 2, 21, 10, 30)


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_sources():
    assert (
        parsed_items[0]["source"]
        == "https://metrarr.granicus.com/ViewPublisher.php?view_id=5"
    )


def test_id():
    assert parsed_items[0]["id"] == (
        "il_metra_board/201802211030/x/metra_february_2018_board_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[12]["links"] == [
        {
            "href": (
                "http://metrarr.granicus.com/AgendaViewer.php" "?view_id=5&clip_id=276"
            ),
            "title": "Agenda",
        },
        {
            "href": (
                "http://metrarr.granicus.com/MinutesViewer.php"
                "?view_id=5&clip_id=276&doc_id="
                "67620acc-fc9b-11e7-8dcb-00505691de41"
            ),
            "title": "Minutes",
        },
        {
            "href": (
                "http://metrarr.granicus.com/MediaPlayer.php" "?view_id=5&clip_id=276"
            ),
            "title": "Video",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] is None
