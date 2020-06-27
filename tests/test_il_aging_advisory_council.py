from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_aging_advisory_council import IlAgingAdvisoryCouncilSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_aging_advisory_council.html"),
    url="https://www2.illinois.gov/aging/PartnersProviders/OlderAdult/Pages/acmeetings.aspx",  # noqa
)
spider = IlAgingAdvisoryCouncilSpider()

freezer = freeze_time("2019-12-23")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Advisory Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 2, 25, 13, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 2, 25, 15, 0)


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "160 N. LaSalle Street, 7th Floor, Chicago",
        "name": "Michael A. Bilandic Building",
    }


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www2.illinois.gov/aging/PartnersProviders/OlderAdult/Documents/Full_OASAC_Minutes_2.25.2019.pdf",  # noqa
            "title": "Minutes",
        },
        {
            "href": "https://www2.illinois.gov/aging/PartnersProviders/Documents/NutritionInnovations_Grant%20Presentation_OASAC.pdf",  # noqa
            "title": "Nutrition Innovations Presentation",
        },
        {
            "href": "https://www2.illinois.gov/aging/PartnersProviders/Documents/HCA_WorkforceSurveyResultsSummary_OASAC.pdf",  # noqa
            "title": "HCA Survey Findings Presentation",
        },
    ]


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www2.illinois.gov/aging/PartnersProviders/OlderAdult/Pages/acmeetings.aspx"  # noqa
    )
