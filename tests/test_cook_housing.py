from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_housing import CookHousingSpider

test_links_response = file_response(
    join(dirname(__file__), "files", "cook_housing_links.html"),
    url="http://thehacc.org/about/",
)
test_detail_response = file_response(
    join(dirname(__file__), "files", "cook_housing_detail.html"),
    url="http://thehacc.org/event/housing-authority-of-cook-county-board-meeting-2-2-2-2-4/",  # noqa
)
test_response = file_response(
    join(dirname(__file__), "files", "cook_housing.html"),
    url="http://thehacc.org/events/2019-10/",
)
spider = CookHousingSpider()

freezer = freeze_time("2019-11-01")
freezer.start()

parsed_res = [item for item in spider.parse(test_links_response)]
parsed_items = [item for item in spider._parse_events(test_response)]
parsed_item = [item for item in spider._parse_detail(test_detail_response)][0]

freezer.stop()


def test_count():
    assert len(parsed_res) == 5
    assert len(parsed_items) == 1


def test_title():
    assert parsed_item["title"] == "Board of Commissioners"


def test_description():
    assert parsed_item["description"] == ""


def test_start():
    assert parsed_item["start"] == datetime(2019, 10, 17, 14, 0)


def test_end():
    assert parsed_item["end"] == datetime(2019, 10, 17, 16, 0)


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_status():
    assert parsed_item["status"] == PASSED


def test_location():
    assert parsed_item["location"] == spider.location


def test_source():
    assert (
        parsed_item["source"]
        == "http://thehacc.org/event/housing-authority-of-cook-county-board-meeting-2-2-2-2-4/"  # noqa
    )


def test_links():
    assert parsed_item["links"] == [
        {
            "title": "Agenda",
            "href": "http://thehacc.org/wp-content/uploads/2019/10/3-OCTOBER-17-2019-BOARD-AGENDA.pdf",  # noqa
        }
    ]


def test_classification():
    assert parsed_item["classification"] == BOARD


def test_all_day():
    assert parsed_item["all_day"] is False
