from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_pharmaceutical_disposal import (
    CookPharmaceuticalDisposalSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "cook_pharmaceutical_disposal.html"),
    url="https://www.cookcountysheriff.org/rx/advisory-committee/",
)
spider = CookPharmaceuticalDisposalSpider()

freezer = freeze_time("2020-10-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Safe Disposal of Pharmaceuticals Advisory Committee"
    )


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 12, 10, 13, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm exact times"


def test_id():
    assert (
        parsed_items[0]["id"]
        == "cook_pharmaceutical_disposal/201912101300/x/"
        + "safe_disposal_of_pharmaceuticals_advisory_committee"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "50 W Washington St, Room 407, Chicago, IL 60602",
        "name": "Daley Center",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.cookcountysheriff.org/rx/advisory-committee/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.cookcountysheriff.org/wp-content/uploads/"
            + "2019/11/Dec.-10-2019-Advisory-Committee-Meeting-Agenda.pdf",
            "title": "Dec. 10 2019 Advisory Committee Meeting Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
