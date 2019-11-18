from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_northwest_home_equity import ChiNorthwestHomeEquitySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_northwest_home_equity.html"),
    url="https://nwheap.com/category/meet-minutes-and-agendas/",
)
spider = ChiNorthwestHomeEquitySpider()

freezer = freeze_time("2019-11-08")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_tests():
    print("Please write some tests for this spider or at least disable this one.")


def test_meeting_count():
    assert len(parsed_items) == 12


def test_date_from_description():
    assert parsed_items[8]["start"] == datetime(2019, 3, 27, 12, 0)


def test_title_upcoming():
    assert parsed_items[10]["title"] == "Board Meeting"


def test_start_upcoming():
    assert parsed_items[10]["start"] == datetime(2019, 11, 14, 6, 30)


def test_end_upcoming():
    assert parsed_items[10]["end"] == datetime(2019, 11, 14, 7, 30)


def test_address_upcoming():
    assert parsed_items[10]["location"] == {"name": "", "address": "3022 N. Harlem, Chicago, IL"}


def test_default_start_time():
    assert parsed_items[9]["start"] == datetime(2019, 3, 14, 12, 0)


def test_no_location():
    assert parsed_items[9]["location"] == {"name": "TBD", "address": ""}


def test_title():
    assert parsed_items[0]["title"] == "October 10, 2019 – Meeting Minutes and Agenda"


def test_description():
    assert parsed_items[0]["description"] == "GOVERNING COMMISSION PUBLIC MEETING Oct"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 10, 10, 12, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 10, 10, 7, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    id = "chi_northwest_home_equity/201910101200/x/october_10_2019_meeting_minutes_and_agenda"
    assert parsed_items[0]["id"] == id


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {"name": "", "address": "3022 N. Harlem, Chicago, IL"}


def test_source():
    assert parsed_items[0]["source"] == "https://nwheap.com/category/meet-minutes-and-agendas/"


def test_links():
    assert parsed_items[0]["links"] == [{
        "href": "https://nwheap.com/2019/10/09/october-10-2019-meeting-minutes-and-agenda/",
        "title": "October 10, 2019 – Meeting Minutes and Agenda"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
