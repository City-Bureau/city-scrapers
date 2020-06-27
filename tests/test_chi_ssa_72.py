from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CANCELLED, COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_72 import ChiSsa72Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_72.html"),
    url="http://www.av72chicago.com/commissioners--meetings.html",
)
spider = ChiSsa72Spider()

freezer = freeze_time("2019-10-29")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Advisory Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 4, 22, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_72/201904221000/x/advisory_commission"


def test_status():
    assert parsed_items[0]["status"] == CANCELLED


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "5053 W. Chicago Ave, Chicago, IL, 60651",
        "name": "Westside Health Authority",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://www.av72chicago.com/commissioners--meetings.html"
    )


def test_links():
    assert parsed_items[1]["links"] == [
        {
            "href": "http://www.av72chicago.com/uploads/9/7/3/6/97363464/av72_may_1_2019_minutes.pdf",  # noqa
            "title": "Meeting Minutes",
        },
        {
            "href": "http://www.av72chicago.com/uploads/9/7/3/6/97363464/may_1_2019_agenda_av72chicago.pdf",  # noqa
            "title": "Agenda",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
