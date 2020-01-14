from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_aging_advisory_council import IlAgingAdvisoryCouncilSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_aging_advisory_council.html"),
    url="https://www2.illinois.gov/aging/PartnersProviders/OlderAdult/Pages/acmeetings.aspx",
)
spider = IlAgingAdvisoryCouncilSpider()

freezer = freeze_time("2019-12-23")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

# def test_tests():
#     print("Please write some tests for this spider or at least disable this one.")
#     assert False
"""
Uncomment below
"""


def test_title():
    assert parsed_items[0]["title"] == "Illinois Department on Aging Advisory Committee Meetings"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 2, 25, 13, 0)


def test_time_notes():
    assert "Committee meetings are held from 1 p.m. - 3 p.m" in parsed_items[0]["time_notes"]


def test_source():
    assert parsed_items[
        0]["source"
           ] == "https://www2.illinois.gov/aging/PartnersProviders/OlderAdult/Pages/acmeetings.aspx"


def test_location():
    assert parsed_items[0]["location"][0] == {
        'address': {
            'Springfield': 'One Natural Resources Way #100',
            'Chicago': '160 N. LaSalle Street, 7th Floor'
        },
        'name': {
            'Springfield': 'Illinois Department on Aging',
            'Chicago': 'Michael A. Bilandic Building'
        }
    }


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
