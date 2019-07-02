from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_43 import ChiSsa43Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_43.html"),
    url="https://rpba.org/ssa-43/",
)
spider = ChiSsa43Spider()

freezer = freeze_time("2019-07-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 26


def test_title():
    assert parsed_items[0]["title"] == "Commission"
    assert parsed_items[5]["title"] == "Emergency Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 14, 2, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm time"


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_43/201901140230/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "https://rpba.org/ssa-43/"


def test_links():
    assert parsed_items[0]["links"] == [{
        "link": "https://rpba.org/wp-content/uploads/2019/01/43-1.14.19-Agenda.pdf",
        "title": "Agenda"
    }, {
        "link": "https://rpba.org/wp-content/uploads/2019/02/43-1.14.19-Minutes.pdf",
        "title": "Minutes"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
