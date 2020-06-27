from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_opioid_response import IlOpioidResponseSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_opioid_response.html"),
    url="https://www.dhs.state.il.us/page.aspx?item=97186",
)
spider = IlOpioidResponseSpider()

freezer = freeze_time("2019-04-16")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Advisory Council"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 4, 15, 13, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 4, 15, 15, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "il_opioid_response/201904151300/x/advisory_council"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "401 S. Clinton Street, 7th Floor Executive Conference Room, Chicago, IL 60607",  # noqa
        "name": "Illinois Department of Human Services Clinton Building",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "https://www.dhs.state.il.us/page.aspx?item=97186"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.dhs.state.il.us/OneNetLibrary/27896/documents/Agenda_04.15.19.pdf",  # noqa
            "title": "Agenda 04.15.19 (pdf)",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
