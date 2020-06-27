from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.il_procurement_policy import IlProcurementPolicySpider

test_response = file_response(
    join(dirname(__file__), "files", "il_procurement_policy.html"),
    url="https://www2.illinois.gov/sites/ppb/Pages/future_board_minutes.aspx",
)
spider = IlProcurementPolicySpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2019-10-07")
freezer.start()

parsed_items = [item for item in spider._upcoming_meetings(test_response)]


def test_count():
    assert len(parsed_items) == 1


def test_title():
    assert parsed_items[0]["title"] == "Procurement Policy Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 10, 15, 10, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_procurement_policy/201910151000/x/procurement_policy_board"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Stratton Office Building",
        "address": "401 S Spring St, Springfield, IL 62704",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www2.illinois.gov/sites/ppb/Pages/future_board_minutes.aspx"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www2.illinois.gov/sites/ppb/Documents/191015%20Agenda.pdf",
            "title": "October 15, 2019 Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


# previous meeting minutes
prev_url = "https://www2.illinois.gov/sites/ppb/Pages/board_minutes.aspx"
test_response2 = file_response(
    join(dirname(__file__), "files", "il_procurement_policy_prev.html"), url=prev_url,
)
parsed_items_prev = sorted(
    [item for item in spider._prev_meetings(test_response2)], key=itemgetter("start")
)
freezer.stop()


def test_count_prev():
    assert len(parsed_items_prev) == 3


def test_title_prev():
    assert parsed_items_prev[0]["title"] == "Procurement Policy Board"


def test_description_prev():
    assert parsed_items_prev[0]["description"] == ""


def test_start_prev():
    assert parsed_items_prev[0]["start"] == datetime(2018, 10, 16, 10, 0)


def test_time_notes_prev():
    assert parsed_items_prev[0]["time_notes"] == ""


def test_id_prev():
    assert (
        parsed_items_prev[0]["id"]
        == "il_procurement_policy/201810161000/x/procurement_policy_board"
    )


def test_status_prev():
    assert parsed_items_prev[2]["status"] == PASSED


def test_location_prev():
    assert parsed_items_prev[0]["location"] == {
        "name": "Stratton Office Building",
        "address": "401 S Spring St, Springfield, IL 62704",
    }


def test_source_prev():
    assert (
        parsed_items_prev[0]["source"]
        == "https://www2.illinois.gov/sites/ppb/Pages/board_minutes.aspx"
    )


def test_links_prev():
    assert parsed_items_prev[0]["links"] == [
        {
            "href": "https://www2.illinois.gov/sites/ppb/Documents/181016%20Minutes.pdf",  # noqa
            "title": "October 16, 2018",
        }
    ]


def test_classification_prev():
    assert parsed_items_prev[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items_prev)
def test_all_day_prev(item):
    assert item["all_day"] is False
