from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.il_investment_policy import IlInvestmentPolicySpider

test_response = file_response(
    join(dirname(__file__), "files", "il_investment_policy.html"),
    url="https://www2.illinois.gov/sites/iipb/Pages/MeetingInformation.aspx",
)
spider = IlInvestmentPolicySpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2019-10-02")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 14


def test_title():
    assert parsed_items[0]["title"] == "Investment Policy Board"
    assert parsed_items[1]["title"] == "Committee on Sudan and Iran Restrictions"
    assert parsed_items[2]["title"] == "Investment Policy Board"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 12, 10, 11, 00)
    assert parsed_items[1]["start"] == datetime(2019, 9, 11, 11, 00)


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == "Confirm start time with agency."


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[1]["status"] == PASSED
    assert parsed_items[2]["status"] == PASSED


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "James R. Thompson Center",
        "address": "100 W. Randolph St., Room 16-503, Chicago, Illinois",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    source = "https://www2.illinois.gov/sites/iipb/Pages/MeetingInformation.aspx"
    assert item["source"] == source


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[1]["links"] == [
        {
            "href": "https://www2.illinois.gov/sites/iipb/Documents/"
            "ISE-CommitteeRevisedAgenda91119.pdf",
            "title": "Committee Agenda 9.11.19",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[1]["classification"] == COMMITTEE
    assert parsed_items[2]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
