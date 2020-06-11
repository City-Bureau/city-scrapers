from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_24 import ChiSsa24Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_24.html"), url="https://rpba.org/ssa-24/",
)
test_detail_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_24_detail.html"),
    url=(
        "https://business.rpba.org/events/details/clark-morse-glenwood-ssa-24-commissioners-meeting-6355"  # noqa
    ),
)
spider = ChiSsa24Spider()

freezer = freeze_time("2019-12-10")
freezer.start()

spider.link_date_map = spider._parse_links(test_response)
parsed_item = [item for item in spider._parse_detail(test_detail_response)][0]

freezer.stop()


def test_title():
    assert parsed_item["title"] == "Commission"


def test_description():
    assert parsed_item["description"] == ""


def test_start():
    assert parsed_item["start"] == datetime(2019, 9, 4, 9, 0)


def test_end():
    assert parsed_item["end"] == datetime(2019, 9, 4, 10, 0)


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_id():
    assert parsed_item["id"] == "chi_ssa_24/201909040900/x/commission"


def test_status():
    assert parsed_item["status"] == PASSED


def test_location():
    assert parsed_item["location"] == {
        "address": "1448 W. Morse Ave. Chicago, IL 60626",
        "name": "Rogers Park Business Alliance",
    }


def test_source():
    assert parsed_item["source"] == test_detail_response.url


def test_links():
    assert parsed_item["links"] == [
        {
            "href": "https://rpba.org/wp-content/uploads/2019/09/24-9.4.19-Agenda.pdf",
            "title": "Agenda",
        },
        {
            "href": "https://rpba.org/wp-content/uploads/2019/11/24-9.4.19-Minutes.pdf",
            "title": "Minutes",
        },
    ]


def test_classification():
    assert parsed_item["classification"] == COMMISSION


def test_all_day():
    assert parsed_item["all_day"] is False
