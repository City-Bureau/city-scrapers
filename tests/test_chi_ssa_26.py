from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_26 import ChiSsa26Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_26.html"),
    url="https://www.edgewater.org/ssa-26/commissionmeetings/",
)
spider = ChiSsa26Spider()

freezer = freeze_time("2019-07-01")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)], key=itemgetter("start")
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 27


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2015, 2, 17, 15, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_26/201502171500/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.edgewater.org/ssa-26/commissionmeetings/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://edgewaterchmb.wpengine.com/wp-content/uploads/2014/03/Agenda-Feb-2015.doc",  # noqa
            "title": "Minutes",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
