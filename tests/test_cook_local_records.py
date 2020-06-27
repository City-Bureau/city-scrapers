from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CANCELLED, COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_local_records import CookLocalRecordsSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_local_records.html"),
    url=(
        "https://cyberdriveillinois.com/departments/archives/records_management/lrc_cook_county_meeting_schedule.html"  # noqa
    ),
)
spider = CookLocalRecordsSpider()

freezer = freeze_time("2019-04-11")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 24


def test_title():
    assert parsed_items[0]["title"] == "Local Records Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 8, 11, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "cook_local_records/201901081100/x/local_records_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == CANCELLED
    assert parsed_items[1]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://cyberdriveillinois.com/departments/archives/records_management/lrc_cook_county_meeting_schedule.html"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://cyberdriveillinois.com/departments/archives/records_management/cclrcmeet/cclrc0119agenda.pdf",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
