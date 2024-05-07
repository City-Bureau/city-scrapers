from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import NOT_CLASSIFIED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_low_income_housing_trust_fund import (
    ChiLowIncomeHousingTrustFundSpider,
)

# Simulate the current date at the time of testing
freezer = freeze_time("2024-05-07")
freezer.start()

# Initialize the spider
spider = ChiLowIncomeHousingTrustFundSpider()
# Simulate a file response with a sample ics file
cal_res = file_response(
    join(dirname(__file__), "files", "chi_low_income_housing_trust_fund.ics"),
    url="https://clihtf.org/?post_type=tribe_events&ical=1&eventDisplay=list",
)
parsed_items = [item for item in spider.parse(cal_res)]

freezer.stop()


# Test for event title
def test_title():
    assert parsed_items[0]["title"] == "Outreach Meeting"


# Test for event start datetime
def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 5, 9, 8, 30)


# Test for event end datetime
def test_end():
    assert parsed_items[0]["end"] == datetime(2024, 5, 9, 9, 30)


# Test for unique event ID
def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_low_income_housing_trust_fund/202405090830/x/outreach_meeting"
    )


# Test for classification of the event
def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


# Test for event status
def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


# Test for event description
def test_description():
    assert parsed_items[0]["description"] == ""


# Test for location details
def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Chicago Low-Income Housing Trust Fund",
        "address": "77 West Washington Street, Suite 719, Chicago, IL 60602",
    }


# Test for links associated with the event
def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://clihtf.org/event/outreach-meeting-4/",
            "title": "Event Details",
        }
    ]


# Test if the event is marked as all day
def test_all_day():
    assert parsed_items[0]["all_day"] is False
