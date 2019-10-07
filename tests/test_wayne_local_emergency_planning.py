from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wayne_local_emergency_planning import WayneLocalEmergencyPlanningSpider

test_response = file_response(
    join(dirname(__file__), "files", "wayne_local_emergency_planning.html"),
    url="https://www.waynecounty.com/departments/hsem/wayne-county-lepc.aspx",
)
spider = WayneLocalEmergencyPlanningSpider()

freezer = freeze_time("2019-10-03")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_tests():
    print("Please write some tests for this spider or at least disable this one.")
    # assert False
    assert True  # disabled this test


"""
Uncomment below
"""


# def test_title():
#    assert parsed_items[0]["title"] == "Local Emergency Planning Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 3, 6, 14, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    EXPECTED_TIME_NOTES = "The Wayne County LEPC meets quarterly. All meetings will be at 2:00 p.m."
    assert parsed_items[0]["time_notes"] == EXPECTED_TIME_NOTES


#  def test_id():
#    EXPECTED_ID = '''wayne_local_emergency_planning/201903061400/'''
#    EXPECTED_ID += '''x/local_emergency_planning_committee'''
#    assert parsed_items[0]["id"] == EXPECTED_ID


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_status1():
    assert parsed_items[1]["status"] == "passed"


def test_status2():
    assert parsed_items[2]["status"] == "passed"


def test_status3():
    assert parsed_items[3]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Wayne County Community College, in the MIPSE Building",
        "address": "21000 Northline Road, Taylor, MI"
    }


def test_source():
    EXPECTED_SOURCE = "https://www.waynecounty.com/departments/hsem/wayne-county-lepc.aspx"
    assert parsed_items[0]["source"] == EXPECTED_SOURCE


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


def test_correct_number_of_items():
    assert len(parsed_items) == 4
