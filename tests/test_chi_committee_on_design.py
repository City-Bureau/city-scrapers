from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_committee_on_design import ChiCommitteeOnDesignSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_committee_on_design.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design.html",
)
spider = ChiCommitteeOnDesignSpider()

freezer = freeze_time("2022-04-11")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Committee on Design Meeting"


def test_description():
    assert parsed_items[0]["description"] == (
        "The Committee on Design is a volunteer group of 24 urban "
        "design professionals organized by the Department of Planning "
        "and Development (DPD) to advise Commissioner Maurice Cox and "
        "DPD staff on design excellence for key development projects "
        "and urban design initiatives."
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 4, 13, 13, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert (
        parsed_items[0]["time_notes"]
        == "Historically, meetings have started at 1:00pm or 1:30pm"
    )


def test_location():
    assert parsed_items[0]["location"] == {"name": "Virtual", "address": "Virtual"}


def test_links():
    assert parsed_items[0]["links"][0] == {
        "href": "https://livestream.com/accounts/28669066/events/9117952",
        "title": "Meeting Link",
    }
    assert len(parsed_items[0]["links"]) == 2
    assert len(parsed_items[1]["links"]) == 1


def test_classification():
    assert parsed_items[0]["classification"] == "COMMITTEE"


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
