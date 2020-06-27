from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_development_fund import ChiDevelopmentFundSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_development_fund.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_developmentfund.html",  # noqa
)
spider = ChiDevelopmentFundSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2018-05-01")
freezer.start()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_meeting_count():
    assert len(parsed_items) == 6


def test_unique_id_count():
    assert len(set([item["id"] for item in parsed_items])) == 6


def test_title():
    assert parsed_items[0]["title"] == "Advisory Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 4, 18)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda for time"


def test_id():
    assert parsed_items[0]["id"] == "chi_development_fund/201804180000/x/advisory_board"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Hall",
        "address": "121 N LaSalle St, Room 1000, Chicago, IL 60602",
    }


def test_sources():
    assert (
        parsed_items[0]["source"]
        == "https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_developmentfund.html"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/dcd/agendas/CDF_Advisor_Board_Agenda_April_2018.pdf",  # noqa
            "title": "Agenda",
        }
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
