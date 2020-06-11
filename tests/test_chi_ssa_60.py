from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_60 import ChiSsa60Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_60.html"),
    url="https://northrivercommission.org/",
)
spider = ChiSsa60Spider()

freezer = freeze_time("2019-10-18")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Economic Development Meeting"


def test_description():
    test_str = (
        "You are invited to join North River Commission and the Albany Park Chamber of"
    )
    assert parsed_items[0]["description"].startswith(test_str)


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 10, 1, 19, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 10, 1, 21, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_ssa_60/201910011900/x/economic_development_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Oso Apartments",
        "address": "3445 W. Montrose Ave. Chicago, IL 60625",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://northrivercommission.org/event/economic-development-meeting/"
    )


def test_links():
    assert parsed_items[0]["links"] == list()


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
