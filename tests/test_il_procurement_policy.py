from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_procurement_policy import IlProcurementPolicySpider

test_response = file_response(
    join(dirname(__file__), "files", "il_procurement_policy.html"),
    url="https://www2.illinois.gov/sites/ppb/Pages/future_board_minutes.aspx",
)
spider = IlProcurementPolicySpider()

freezer = freeze_time("2019-10-07")
freezer.start()

parsed_items = [item for item in spider._upcoming_meetings(test_response)]


def test_len():
    assert len(parsed_items) == 1


def test_title():
    assert parsed_items[0]["title"] == "Procurement Policy Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 10, 15, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "End time not specified"


def test_id():
    assert parsed_items[0]["id"] == "il_procurement_policy/201910151000/x/procurement_policy_board"


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Stratton Office Building",
        "address": "401 S Spring St, Springfield, IL 62704"
    }


def test_source():
    assert parsed_items[0]["source"].startswith("https://www2.illinois.gov/sites/ppb/Pages/future")


def test_links():
    assert parsed_items[0]["links"] == [{
        'href': 'https://www2.illinois.gov/sites/ppb/Documents/191015%20Agenda.pdf',
        'title': 'October 15, 2019 Agenda'
    }]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


# previous meeting minutes
prev_url = "https://www2.illinois.gov/sites/ppb/Pages/board_minutes.aspx"
test_response2 = file_response(
    join(dirname(__file__), "files", "il_procurement_policy_prev.html"),
    url=prev_url,
)
parsed_items_prev = [item for item in spider._prev_meetings(test_response2)]
freezer.stop()


def prev_test_title():
    assert parsed_items_prev[0]["title"] == "2018 Board Meeting Minutes"


def prev_test_description():
    assert parsed_items_prev[0]["description"] == ""


def prev_test_start():
    assert parsed_items_prev[0]["start"] == datetime(2019, 10, 15, 10, 0)


def prev_test_end():
    assert parsed_items_prev[0]["end"] is None


def prev_test_time_notes():
    assert parsed_items_prev[0]["time_notes"] == "End time not specified"


def prev_test_id():
    assert parsed_items_prev[0]["id"].startswith("il_procurement_policy/201801171000/x/")


def prev_test_status():
    assert parsed_items_prev[0]['status'] == PASSED


def prev_test_location():
    assert parsed_items_prev[0]["location"] == {
        "name": "Stratton Office Building",
        "address": "401 S Spring St, Springfield, IL 62704"
    }


def prev_test_source():
    assert parsed_items_prev[0]["source"].startswith("https://www2.illinois.gov/sites/ppb/Pages/")


def prev_test_links():
    assert parsed_items_prev[0]["links"] == [{
        'href': 'https://www2.illinois.gov/sites/ppb/Documents/180117%20Minutes.pdf',
        'title': 'Feburary 27, 2019'
    }]


def prev_test_classification():
    assert parsed_items_prev[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items_prev)
def prev_test_all_day(item):
    assert item["all_day"] is False
