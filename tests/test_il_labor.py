from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_labor import IlLaborSpider

freezer = freeze_time("2018-12-12")
freezer.start()
test_response = file_response(
    join(dirname(__file__), "files", "il_labor.html"),
    url="https://www.illinois.gov/ilrb/meetings/Pages/default.aspx",
)
spider = IlLaborSpider()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_count():
    assert len(parsed_items) == 3


def test_title():
    assert parsed_items[0]["title"] == "Local Panel"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 12, 11, 9)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "il_labor/201812110900/x/local_panel"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.illinois.gov/ilrb/Documents/LPAgenda.pdf",
            "title": "Agenda",
        }
    ]


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.illinois.gov/ilrb/meetings/Pages/default.aspx"
    )
