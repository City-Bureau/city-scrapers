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

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

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
    assert parsed_items[0]["source"] == "https://www2.illinois.gov/sites/ppb/Pages/future_board_minutes.aspx"


def test_links():
    assert parsed_items[0]["links"][0]['href'] == 'https://www2.illinois.gov/sites/ppb/Documents/191015%20Agenda.pdf'


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False