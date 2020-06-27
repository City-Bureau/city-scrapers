from datetime import datetime
from os.path import dirname, join
from unittest.mock import MagicMock

import pytest
from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_library import ChiLibrarySpider

freezer = freeze_time("2018-12-20")
freezer.start()
session = MagicMock()
res_mock = MagicMock()
res_mock.status_code = 200
session.get.return_value = res_mock
test_response = file_response(
    join(dirname(__file__), "files", "chi_library.html"),
    url="https://www.chipublib.org/board-of-directors/board-meeting-schedule/",
)
spider = ChiLibrarySpider(session=session)
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 15, 9)


def test_id():
    assert parsed_items[0]["id"] == "chi_library/201901150900/x/board_of_directors"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "400 S. State Street Chicago, IL",
        "name": "Harold Washington Library Center",
    }


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://www.chipublib.org/news/board-of-directors-meeting-agenda-january-15-2019/",  # noqa
        },
        {
            "title": "Minutes",
            "href": "https://www.chipublib.org/news/board-of-directors-meeting-minutes-january-15-2019/",  # noqa
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert (
        item["source"]
        == "https://www.chipublib.org/board-of-directors/board-meeting-schedule/"
    )
