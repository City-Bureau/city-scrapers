from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_35 import ChiSsa35Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_35.html"),
    url="https://www.lincolnparkchamber.com/businesses/"
    + "special-service-areas/lincoln-avenue-ssa/ssa-administration/",
)
spider = ChiSsa35Spider()

freezer = freeze_time("2021-1-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 1, 26)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_35/202101260000/x/commission"


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Confirm with agency",
        "address": "",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.lincolnparkchamber.com/businesses/"
        + "special-service-areas/lincoln-avenue-ssa/ssa-administration/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {"href": None, "title": "Tuesday January 26 2021"}
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
