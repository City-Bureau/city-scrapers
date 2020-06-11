from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_62 import ChiSsa62Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_62.html"),
    url="http://escc60646.com/our_events/?date1=all",
)
spider = ChiSsa62Spider()

freezer = freeze_time("2019-10-14")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 6


def test_title():
    assert parsed_items[0]["title"] == "Advisory Commission Meeting"
    assert parsed_items[1]["title"] == "Board of Directors Meeting"
    assert parsed_items[2]["title"] == "Advisory Commission Meeting"
    assert parsed_items[3]["title"] == "Board of Directors Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[1]["description"] == ""
    assert parsed_items[2]["description"] == ""
    assert parsed_items[3]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 7, 16, 7, 30)
    assert parsed_items[1]["start"] == datetime(2019, 9, 11, 13, 30)
    assert parsed_items[2]["start"] == datetime(2019, 9, 17, 7, 30)
    assert parsed_items[3]["start"] == datetime(2019, 10, 9, 13, 30)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] is None
    assert parsed_items[2]["end"] is None
    assert parsed_items[3]["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == ""


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[1]["status"] == PASSED
    assert parsed_items[2]["status"] == PASSED
    assert parsed_items[3]["status"] == PASSED
    assert parsed_items[4]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "4747 W. Peterson, 2d Floor Conference Room, Chicago, IL",
    }
    assert parsed_items[1]["location"] == {
        "name": "Wintrust Bank",
        "address": "4343 W. Peterson, Chicago, IL",
    }
    assert parsed_items[2]["location"] == {
        "name": "",
        "address": "4747 W. Peterson, 2d Floor Conference Room, Chicago, IL",
    }
    assert parsed_items[3]["location"] == {
        "name": "Wintrust Bank",
        "address": "4343 W. Peterson, Chicago, IL",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "http://escc60646.com/our_events/?event_id1=118981"
    )
    assert (
        parsed_items[1]["source"] == "http://escc60646.com/our_events/?event_id1=119034"
    )
    assert (
        parsed_items[2]["source"] == "http://escc60646.com/our_events/?event_id1=118983"
    )
    assert (
        parsed_items[3]["source"] == "http://escc60646.com/our_events/?event_id1=119036"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://escc60646.com/wp-content/uploads/SSA-Commission-Agenda-16jul2019.pdf",  # noqa
            "title": "Agenda",
        }
    ]
    assert parsed_items[1]["links"] == []
    assert parsed_items[2]["links"] == [
        {
            "href": "http://escc60646.com/wp-content/uploads/SSA-Commission-Agenda-17sep2019.pdf",  # noqa
            "title": "Agenda",
        }
    ]
    assert parsed_items[3]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE
    assert parsed_items[1]["classification"] == BOARD
    assert parsed_items[2]["classification"] == ADVISORY_COMMITTEE
    assert parsed_items[3]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
