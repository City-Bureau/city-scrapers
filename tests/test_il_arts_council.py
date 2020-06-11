from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_arts_council import IlArtsCouncilSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_arts_council.html"),
    url="http://www.arts.illinois.gov/about-iac/governance/council-meetings",
)
spider = IlArtsCouncilSpider()

freezer = freeze_time("2019-10-25")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Agency Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 5, 15, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "il_arts_council/202005150000/x/agency_board"


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {"address": "TBA", "name": "TBA"}


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://www.arts.illinois.gov/about-iac/governance/council-meetings"
    )  # noqa


def test_links():
    assert parsed_items[8]["links"] == [
        {
            "href": "http://www.arts.illinois.gov/sites/default/files/content/11-16-18%20COUNCILMINUTES.pdf",  # noqa
            "title": "11-16-18 COUNCILMINUTES.pdf",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
