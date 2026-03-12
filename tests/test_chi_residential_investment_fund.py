from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_residential_investment_fund import (
    ChiResidentialInvestmentFundSpider,
)


@pytest.fixture
def test_response():
    return file_response(
        join(dirname(__file__), "files", "chi_residential_investment_fund.html"),
        url="https://www.chicagorif.com/about",
    )


@pytest.fixture
def parsed_items(test_response):
    spider = ChiResidentialInvestmentFundSpider()
    with freeze_time("2026-03-11"):
        return [item for item in spider.parse(test_response)]


def test_count(parsed_items):
    assert len(parsed_items) == 5


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Board Meeting"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 1, 13, 0, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "passed"


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "City Hall, Rm. 1003A",
        "address": "121 N LaSalle St, Chicago, IL 60610",
    }


def test_source(parsed_items):
    assert parsed_items[0]["source"] == "https://www.chicagorif.com/about"


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.chicagorif.com/_files/ugd/"
            "b6ef1a_c1fa809c87b649309a93a5ae8d3f25be.pdf",
            "title": "Agenda",
        },
        {
            "href": "https://www.chicagorif.com/_files/ugd/"
            "b6ef1a_169be7ab4a834cbeb759bf7caae37136.pdf",
            "title": "Minutes",
        },
    ]


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"]
        == "chi_residential_investment_fund/202601130000/x/board_meeting"
    )


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD


def test_all_day(parsed_items):
    for item in parsed_items:
        assert item["all_day"] is False


def test_aprli_typo_is_parsed(parsed_items):
    assert parsed_items[3]["start"] == datetime(2026, 4, 14, 0, 0)


def test_unrelated_rich_text_block_is_ignored(parsed_items):
    assert all(item["title"] == "Board Meeting" for item in parsed_items)
