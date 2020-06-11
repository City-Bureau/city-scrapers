from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_boardofethics import ChiBoardOfEthicsSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_boardofethics.html"),
    url="https://www.chicago.gov/city/en/depts/ethics/supp_info/minutes.html",
)

freezer = freeze_time("2020-01-06")
freezer.start()

spider = ChiBoardOfEthicsSpider()

parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_items():
    assert len(parsed_items) == 14


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"


def test_description():
    assert (
        parsed_items[-1]["description"]
        == "All 2020 Meetings will be held at 3:00 PM and typically last about 2 hours. Meetings are held at the City of Chicago Board of Ethics, 740 N. Sedgwick, Ste. 500, Chicago, IL 60654-8488"  # noqa
    )


def test_start():
    assert parsed_items[-1]["start"] == datetime(2020, 12, 14, 15, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"] == "chi_boardofethics/201911151200/x/board_of_directors"
    )


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City of Chicago Board of Ethics",
        "address": "740 N. Sedgwick, Ste. 500, Chicago, IL 60654-8488",
    }


def test_sources():
    assert (
        parsed_items[0]["source"]
        == "https://www.chicago.gov/city/en/depts/ethics/supp_info/minutes.html"
    )


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD
