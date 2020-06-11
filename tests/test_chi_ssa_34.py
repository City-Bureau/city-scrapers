from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_34 import ChiSsa34Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_34.html"),
    url="https://exploreuptown.org/ssa/",
)
spider = ChiSsa34Spider()

freezer = freeze_time("2019-06-27")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 21


def test_title():
    assert parsed_items[0]["title"] == "Advisory Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 22, 16, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_34/201901221630/x/advisory_commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "https://exploreuptown.org/ssa/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://exploreuptown.org/wp-content/uploads/2019/03/2019-0122-SSA-34-Commission-Minutes.pdf",  # noqa
            "title": "Minutes",
        },
        {
            "href": "https://exploreuptown.org/wp-content/uploads/2019/01/2019-0122-Advisory-Commission-Meeting-Agenda.pdf",  # noqa
            "title": "Agenda",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
