from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_board_ethics import CookBoardEthicsSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_board_ethics.html"),
    url="https://www.cookcountyil.gov/event/cook-county-board-ethics-meeting-3",
)
spider = CookBoardEthicsSpider()

freezer = freeze_time("2019-10-9")
freezer.start()
item = spider._parse_event(test_response)
freezer.stop()


def test_title():
    assert item["title"] == "Board of Ethics"


def test_start():
    assert item["start"] == datetime(2019, 8, 29, 14)


def test_end():
    assert item["end"] == datetime(2019, 8, 29, 16)


def test_time_notes():
    assert item["time_notes"] == ""


def test_id():
    assert item["id"] == "cook_board_ethics/201908291400/x/board_of_ethics"


def test_all_day():
    assert item["all_day"] is False


def test_classification():
    assert item["classification"] == BOARD


def test_status():
    assert item["status"] == PASSED


def test_location():
    assert item["location"] == {
        "name": "",
        "address": "69 W. Washington Street, Suite 3040 Chicago IL 60602",
    }


def test_sources():
    assert (
        item["source"]
        == "https://www.cookcountyil.gov/event/cook-county-board-ethics-meeting-3"
    )


def test_description():
    assert item["description"] == ""


def test_links():
    assert item["links"] == []
