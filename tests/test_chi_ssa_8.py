from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_8 import ChiSsa8Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_8.html"),
    url="https://lakevieweast.com/ssa-8/",
)
spider = ChiSsa8Spider()

freezer = freeze_time("2020-07-29")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Special Meeting"
    assert parsed_items[3]["title"] == "2021 budget meeting"


def test_description():
    assert parsed_items[0]["description"] == "Special Meeting"
    assert parsed_items[3]["description"] == "2021 budget meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 2, 25, 0, 0)
    assert parsed_items[3]["start"] == datetime(2020, 7, 23, 0, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2020, 2, 25, 2, 0)
    assert parsed_items[0]["end"] == datetime(2020, 7, 23, 2, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_8/202002250000/x/special_meeting"
    assert parsed_items[3]["id"] == "chi_ssa_8/202007230000/x/2021_budget_meeting"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "LVECC office, 3138 N. Broadway",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://lakevieweast.com/ssa-8/"


def test_links():
    assert parsed_items[0]["links"] == [{"href": "", "title": ""}]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
