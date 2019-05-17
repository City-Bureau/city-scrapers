from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wayne_ethics_board import WayneEthicsBoardSpider

test_response = file_response(
    join(dirname(__file__), "files", "wayne_ethics_board.html"),
    url="https://www.waynecounty.com/boards/ethicsboard/documents.aspx",
)
spider = WayneEthicsBoardSpider()

freezer = freeze_time("2019-05-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 30


def test_title():
    assert parsed_items[0]["title"] == "Ethics Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 2, 20, 9, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm time"


def test_id():
    assert parsed_items[0]["id"] == "wayne_ethics_board/201902200900/x/ethics_board"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"
                           ] == "https://www.waynecounty.com/boards/ethicsboard/documents.aspx"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            'href': 'https://www.waynecounty.com/documents/ethicsboard/ethics_agenda022019.pdf',
            'title': 'Agenda'
        },
        {
            'href':
                'https://www.waynecounty.com/documents/ethicsboard/ethics_board_minutes_2-20-19.pdf',  # noqa
            'title': 'Minutes'
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
