from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.il_board_of_examiners import IlBoardOfExaminersSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_board_of_examiners.html"),
    url="https://www.ilboe.org/board-information/board-meetings/",
)
spider = IlBoardOfExaminersSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2019-09-13")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 4


def test_title():
    assert parsed_items[0]["title"] == "Illinois Board of Examiners"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 7, 24, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_board_of_examiners/201907241000/x/illinois_board_of_examiners"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "1120 E. Diehl Road, Suite 165, Naperville, IL 60563",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.ilboe.org/board-information/board-meetings/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.ilboe.org/wp-content/uploads/2019/07/July-24-2019-Agenda.pdf",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_all_day():
    assert parsed_items[0]["all_day"] is False
