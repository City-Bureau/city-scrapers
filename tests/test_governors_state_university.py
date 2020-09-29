from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.governors_state_university import GovernorsStateUniversitySpider

test_response = file_response(
    join(dirname(__file__), "files", "governors_state_university.html"),
    url="https://www.govst.edu/BOT-Meetings/",
)
spider = GovernorsStateUniversitySpider()

freezer = freeze_time("2020-09-26")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    # br-separated
    assert parsed_items[0]["title"] == "Budget and Finance Committee Meeting"
    # div-separated
    assert parsed_items[2]["title"] == "Human Resources Committee Meeting"
    # no title, we fall back to date
    assert parsed_items[4]["title"] == "February 14, 2020"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 1, 27, 9, 0)
    assert parsed_items[2]["start"] == datetime(2020, 2, 7, 9, 0)
    assert parsed_items[4]["start"] == datetime(2020, 2, 14, 8, 30)
    # this will be 2020-05-15 if postponed events were properly filtered out
    assert parsed_items[10]["start"] == datetime(2020, 5, 15, 9, 0)
    # starting in 2018, sometimes dates do not have years. In case this starts up
    # again, check that these properly get 2018 as their year
    assert parsed_items[27]["start"] == datetime(2018, 2, 22, 9, 0)


def test_end():
    # unused
    assert parsed_items[0]["end"] == None


def test_time_notes():
    # unused
    assert parsed_items[0]["time_notes"] == ""


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Engbretson Hall",
        "address": "1 University Pkwy,\nUniversity Park, IL 60484"
    }
    assert parsed_items[2]["location"] == {
        "name": "70 W. Madison Street",
        "address": "70 W. Madison Street\nSuite 4300\nChicago, IL"
    }
    assert parsed_items[7]["location"] == {
        "name": "Zoom",
        "address": "Zoom"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.govst.edu/BOT-Meetings/"


def test_links():
    # normal fully populated row: one agenda, one minutes
    assert parsed_items[0]["links"] == [{
        "href": "https://www.govst.edu/uploadedFiles/About/University_Governance/Board_of_Trustees/budget and finance committee agenda, 1-27-19, FINAL.pdf",
        "title": "Budget and Finance Committee Meeting Agenda, 1-27-20"
    }, {
        "href": "https://www.govst.edu/uploadedFiles/About/University_Governance/Board_of_Trustees/approved minutes - b and f committee meeting, 1-27-20 - approved at 3-23-20 b and f committee meeting - FINAL.pdf",
        "title": "1-27-20 Budget and Finance Committee - approved meeting minutes"
    }]
    # agenda + notification in column 3
    assert parsed_items[5]["links"] == [{
        "href": "https://www.govst.edu/uploadedFiles/About/University_Governance/Board_of_Trustees/agenda, executive committee meeting, 3-16-20(1).pdf",
        "title": "Executive Committee Meeting Agenda, 3-16-20"
    }, {
        "href": "https://www.govst.edu/uploadedFiles/About/University_Governance/Board_of_Trustees/notification regarding march 16, 2020 executive committee meeting, 3-15-20 - FINAL.docx.pdf",
        "title": "Notification Regarding March 16, 2020 Executive Committee Meeting"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[1]["classification"] == BOARD
    assert parsed_items[4]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
