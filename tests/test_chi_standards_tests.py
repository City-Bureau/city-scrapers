from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_standards_tests import ChiStandardsTestsSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_standards_tests.html"),
    url="https://www.chicago.gov/city/en/depts/bldgs/supp_info/committee_on_standardsandtests.html",  # noqa
)
spider = ChiStandardsTestsSpider()

freezer = freeze_time("2019-10-19")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_result_count():
    assert len(parsed_items) == 34


def test_title():
    assert parsed_items[0]["title"] == "Committee on Standards and Tests"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 16, 13, 30)
    assert parsed_items[3]["start"] == datetime(2019, 10, 16, 13, 30)
    assert parsed_items[-1]["start"] == datetime(2017, 12, 20, 13, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Confirm details with the agency"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Hall",
        "address": "121 North LaSalle Street, Room 906, Chicago, IL 60602",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.chicago.gov/city/en/depts/bldgs/supp_info/committee_on_standardsandtests.html"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[1]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/bldgs/general/Standards_Tests/S&T%20Decisions%20April%202019.pdf",  # noqa
            "title": "Decisions",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
