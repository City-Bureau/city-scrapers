from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_28 import ChiSsa28Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_28.html"),
    url="https://sixcorners.com/ssa28",
)
spider = ChiSsa28Spider()

freezer = freeze_time("2019-10-29")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Six Corners Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 17, 13, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_28/201901171330/x/six_corners_commission"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Portage Arts Lofts",
        "address": "4041 N. Milwaukee Ave. #302, Chicago, IL 60641",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://sixcorners.com/ssa28"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://docs.google.com/document/d/1m6IIG0el8bJt1Bn8ebgDHAmAfCFdyI-YRd1e7Ycim8Y/edit?usp=sharing",  # noqa
            "title": "agenda",
        },
        {
            "href": "https://sixcorners.com/s/1_17_19-SSA-Minutes-reformatted.pdf",
            "title": "minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
