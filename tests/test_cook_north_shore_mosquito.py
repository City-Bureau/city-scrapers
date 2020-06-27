from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_north_shore_mosquito import CookNorthShoreMosquitoSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_north_shore_mosquito.html"),
    url="https://www.nsmad.com/news-events/board-meetings/",
)
spider = CookNorthShoreMosquitoSpider()

freezer = freeze_time("2019-05-08")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 10, 19, 0)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "cook_north_shore_mosquito/201901101900/x/board_of_trustees"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "NSMAD Office",
        "address": "117 Northfield Road, Northfield, IL 60093",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "https://www.nsmad.com/news-events/board-meetings/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.nsmad.com/wp-content/uploads/2019/02/2-Jan1019-minutes.pdf",  # noqa
            "title": "Minutes",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
