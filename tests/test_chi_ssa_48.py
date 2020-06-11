from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_48 import ChiSsa48Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_48.html"),
    url="https://oldtownchicago.org/ssa-48/",
)
spider = ChiSsa48Spider()

freezer = freeze_time("2020-01-04")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 9, 17, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 1, 9, 19, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_48/201901091730/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Wintrust Bank Old Town",
        "address": "100 W North Avenue Chicago, IL",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://oldtownchicago.org/ssa-48/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Final Minutes 1/09/19",
            "href": "https://oldtownchicago.org/wp-content/uploads/2019/07/2019-SSA-48-Commission-Minutes-01-09-2019.docx",  # noqa
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
