from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_school_community_action_council import (
    ChiSchoolCommunityActionCouncilSpider,
)

freezer = freeze_time("2018-06-01")
freezer.start()
test_response = file_response(
    join(dirname(__file__), "files", "chi_school_community_action_council.html"),
    url="http://cps.edu/FACE/Pages/CAC.aspx",
)
spider = ChiSchoolCommunityActionCouncilSpider()
parsed_items = [item for item in spider.parse(test_response)]
current_month_number = datetime.today().month
freezer.stop()


def test_num_items():
    assert len(parsed_items) == (13 - current_month_number) * 8


def test_title():
    assert parsed_items[0]["title"] == "Austin Community Action Council"


def test_start_time():
    assert parsed_items[0]["start"] == datetime(2018, 6, 12, 17, 30)


def test_end_time():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_school_community_action_council/201806121730/x/austin_community_action_council"  # noqa
    )


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Michele Clark HS",
        "address": "5101 W Harrison St. Chicago, IL",
    }


def test_source():
    assert parsed_items[1]["source"] == "https://cacbronzeville.weebly.com/"


@pytest.mark.parametrize("item", parsed_items)
def test_links(item):
    assert item["links"] == []


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMITTEE
