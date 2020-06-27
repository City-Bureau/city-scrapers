from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_transit import ChiTransitSpider

freezer = freeze_time("2018-01-01")
freezer.start()

test_response = file_response(
    join(dirname(__file__), "files", "chi_transit.html"),
    url="https://www.transitchicago.com/board/notices-agendas-minutes/",
)
spider = ChiTransitSpider()
parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_meeting_count():
    assert len(parsed_items) == 23


def test_unique_id_count():
    assert len(set([item["id"] for item in parsed_items])) == 23


def test_title():
    assert parsed_items[0]["title"] == "Employee Retirement Review Committee Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 6, 15, 14, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2018, 6, 15, 17, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "End estimated 3 hours after start time"


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_transit/201806151400/x/employee_retirement_review_committee_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Chicago Transit Authority 2nd Floor Boardroom",
        "address": "567 West Lake Street Chicago, IL 60661",
    }


def test_sources():
    assert (
        parsed_items[0]["source"]
        == "https://www.transitchicago.com/board/notices-agendas-minutes/"
    )


def test_documents():
    assert parsed_items[0]["links"] == [
        {
            "title": "Meeting Notice",
            "href": "http://www.transitchicago.com/assets/1/21/061818_ERR_Notice.pdf?20564",  # noqa
        },
        {
            "title": "Agenda",
            "href": "http://www.transitchicago.com/assets/1/21/061818_ERR_Agenda.pdf?20565",  # noqa
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
