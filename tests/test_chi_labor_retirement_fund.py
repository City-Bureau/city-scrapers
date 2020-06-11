from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, CANCELLED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_labor_retirement_fund import ChiLaborRetirementFundSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_labor_retirement_fund.html"),
    url="http://www.labfchicago.org/agendas-minutes",
)
spider = ChiLaborRetirementFundSpider()

freezer = freeze_time("2019-02-10")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 25


def test_title():
    assert parsed_items[0]["title"] == "Retirement Board"
    assert parsed_items[4]["title"] == "Special Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 12, 17, 9)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_labor_retirement_fund/201912170900/x/retirement_board"
    )


def test_status():
    assert parsed_items[16]["status"] == CANCELLED
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "http://www.labfchicago.org/agendas-minutes"


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[13]["links"] == [
        {
            "href": "http://www.labfchicago.org/assets/1/33/Special_Meeting_Agenda_2019.02.06_to_post.pdf",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
