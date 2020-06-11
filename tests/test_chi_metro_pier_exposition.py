from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, CANCELLED, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_metro_pier_exposition import ChiMetroPierExpositionSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_metro_pier_exposition.html"),
    url="http://www.mpea.com/mpea-board-members/",
)
spider = ChiMetroPierExpositionSpider()

freezer = freeze_time("2019-04-15")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 17


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"
    assert parsed_items[10]["title"] == "Audit Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 1, 23, 9)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Refer to notice for start time"


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_metro_pier_exposition/201801230900/x/board_of_directors"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[1]["status"] == CANCELLED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "http://www.mpea.com/mpea-board-members/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://www.mpea.com/wp-content/uploads/2017/12/January_2018_Board_Notice-1.pdf",  # noqa
            "title": "Notice",
        },
        {
            "href": "http://www.mpea.com/wp-content/uploads/2018/01/MPEA_-Board_Agenda_January_23_2018.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "http://www.mpea.com/wp-content/uploads/2018/03/MPEA_Board_Minutes_Regular_Session_January_23_2018_Final.pdf",  # noqa
            "title": "Minutes",
        },
        {
            "href": "http://www.mpea.com/wp-content/uploads/2018/02/January-2018-Financials-Combined-Operating-Results.pdf",  # noqa
            "title": "Financial Results",
        },
        {
            "href": "http://www.mpea.com/wp-content/uploads/2018/02/January-2018-Tax-Collections.pdf",  # noqa
            "title": "Tax Collections",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[10]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
