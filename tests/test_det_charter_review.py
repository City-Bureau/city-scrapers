from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import FORUM, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_charter_review import DetCharterReviewSpider

test_response = file_response(
    join(dirname(__file__), "files", "det_charter_review.json"),
    url=(
        "https://detroitmi.gov/events/detroit-charter-revision-commission-meeting-economic-growth-development-3-20-19"  # noqa
    ),
)
spider = DetCharterReviewSpider()

freezer = freeze_time("2019-04-23")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Citizen Focus Group: Equitable Planning & Zoning"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 7, 10, 17, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 7, 10, 19, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0][
        "id"] == "det_charter_review/201907101730/x/citizen_focus_group_equitable_planning_zoning"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Edison Public Library",
        "address": "18400 Joy Rd, Detroit, MI 48228, USA",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://sites.google.com/view/detroitcharter2018"


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == FORUM


def test_all_day():
    assert parsed_items[0]["all_day"] is False
