from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_south_mosquito import CookSouthMosquitoSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_south_mosquito.html"),
    url="https://sccmad.org/",
)
spider = CookSouthMosquitoSpider()

freezer = freeze_time("2019-07-10")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)], key=itemgetter("start")
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 17


def test_title():
    assert parsed_items[0]["title"] == "Board of Trustees"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 4, 8, 16, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm time"


def test_id():
    assert (
        parsed_items[0]["id"] == "cook_south_mosquito/201904081600/x/board_of_trustees"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "https://sccmad.org/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Minutes",
            "href": "https://sccmad.org/images/minutes/april-8-2019-minutes.pdf",
        }
    ]
    assert parsed_items[4]["links"] == [
        {
            "title": "Agenda",
            "href": "https://sccmad.org/images/agenda/July-2019-agenda.pdf",
        }
    ]
    assert parsed_items[-1]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_all_day():
    assert parsed_items[0]["all_day"] is False
