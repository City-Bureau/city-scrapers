from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_fire_benefit_fund import ChiFireBenefitFundSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_fire_benefit_fund.html"),
    url="http://www.fabf.org/Meetings.html",
)
spider = ChiFireBenefitFundSpider()

freezer = freeze_time("2019-04-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 16


def test_title():
    assert parsed_items[0]["title"] == "Retirement Board"
    assert parsed_items[-3]["title"] == "Investment Committee"
    assert parsed_items[-2]["title"] == "Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 25)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda for meeting time"


def test_id():
    assert (
        parsed_items[0]["id"] == "chi_fire_benefit_fund/201901250000/x/retirement_board"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "http://www.fabf.org/Meetings.html"


def test_links():
    assert parsed_items[-3]["links"] == [
        {
            "href": "http://www.fabf.org/PDF/Agendas/02-19-19INVST.pdf",
            "title": "Investment Agenda",
        },
        {
            "href": "http://www.fabf.org/PDF/Minutes/02-19-2019INVST.pdf",
            "title": "Investment Minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[-1]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
