from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import PASSED, COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_north_river_mental_health import (
    ChiNorthRiverMentalHealthSpider,
)

test_minutes_response = file_response(
    join(dirname(__file__), "files", "chi_north_river_mental_health_minutes.html"),
    url="https://www.northriverexpandedmentalhealthservicescommission.org/minutes.html",
)
test_index_response = file_response(
    join(dirname(__file__), "files", "chi_north_river_mental_health_index.html"),
    url="https://www.northriverexpandedmentalhealthservicescommission.org/index.html",
)

spider = ChiNorthRiverMentalHealthSpider()

freezer = freeze_time("2020-08-27")
freezer.start()

parsed_minutes_items = [item for item in spider.parse(test_minutes_response)]
parsed_index_items = [item for item in spider.parse(test_index_response)]

freezer.stop()


def test_start():
    assert parsed_minutes_items[0]["start"] == datetime(2020, 1, 15, 19, 0)
    assert parsed_index_items[0]["start"] == datetime(2020, 8, 26, 18, 0)


def test_id():
    assert (
        parsed_minutes_items[0]["id"] == "chi_north_river_mental_health/202001151900/x/"
        "north_river_emhsp_governing_commission"
    )
    assert (
        parsed_index_items[0]["id"] == "chi_north_river_mental_health/202008261800/x/"
        "north_river_emhsp_governing_commission"
    )


def test_location():
    assert parsed_minutes_items[0]["location"] == {
        "name": "North River EMHSP governing commission office",
        "address": "3525 W. Peterson Ave, #306 Chicago, Il 60659",
    }
    assert parsed_index_items[0]["location"] == {
        "name": "Place: ",
        "address": "Zoom Meeting",
    }


def test_source():
    assert (
        parsed_minutes_items[0]["source"]
        == "https://www.northriverexpandedmentalhealthservicescommission.org/"
        "minutes.html"
    )
    assert (
        parsed_index_items[0]["source"]
        == "https://www.northriverexpandedmentalhealthservicescommission.org/"
        "index.html"
    )


def test_links():
    assert parsed_minutes_items[0]["links"] == [
        {
            "href": "https://www.northriverexpandedmentalhealthservicescommission.org/"
            "uploads/3/4/8/8/34884940/meeting_59_january_15_2020_docx.docx",
            "title": "Meeting 59 - January 15th, 2020",
        }
    ]
    assert parsed_index_items[0]["links"] == [
        {"title": "NOTICE", "href": "/agenda.html"},
        {
            "title": "UPCOMING AGENDA",
            "href": "/uploads/3/4/8/8/34884940/nremhsp_finance_com._aug._agenda.pdf",
        },
    ]


def test_status():
    assert parsed_minutes_items[0]["status"] == PASSED
    assert parsed_index_items[0]["status"] == PASSED


@pytest.mark.parametrize("item", parsed_minutes_items + parsed_index_items)
class TestParametrized:
    def test_title(self, item):
        assert item["title"] == "North River EMHSP governing commission"

    def test_description(self, item):
        assert item["description"] == ""

    def test_end(self, item):
        assert item["end"] is None

    def test_time_notes(self, item):
        assert item["time_notes"] == ""

    def test_classification(self, item):
        assert item["classification"] == COMMISSION

    def test_all_day(self, item):
        assert item["all_day"] is False
