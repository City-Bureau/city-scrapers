from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_public_health import IlPublicHealthSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_public_health.html"),
    url="http://www.dph.illinois.gov/events/",
)
spider = IlPublicHealthSpider()

freezer = freeze_time("2019-05-20")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 10


def test_title():
    assert parsed_items[0]["title"] == "PANDAS/PANS Advisory Council"
    assert parsed_items[-1]["title"] == "Perinatal Advisory Committee"


def test_description():
    assert parsed_items[1]["description"] == (
        "VIDEO CONFERENCE\n"
        "525 W. Jefferson St., 4th Floor Video Conference Room, Springfield, IL\n"
        "122 S. Michigan Ave., Conference Room 711, 7th Floor, Chicago, IL\n"
        "Marion Regional Office, 2309 W. Main Street, Marion, IL\n"
        "West Chicago Regional Office, 245 W. Roosevelt, Bldg. 5, West Chicago, IL\n"
        "10:00 a.m. – 12:00 p.m.\n"
        "Interested persons may contact Elaine Huddleston in the Office of Health Care Regulations, Division of Health Care Facilities and Programs at\n"  # noqa
        "217-782-0483."
    )
    assert parsed_items[-1]["description"] == (
        "Meeting Agenda TBA\n"
        "CONFERENCE ROOMS\n"
        "69 West Washington St., 35th Floor, Chicago\n"
        "535 West Jefferson St., 5th Floor, Springfield\n"
        "Conference Call Information\n"
        "Conference Call-In#: 888.494.4032\n"
        "Access Code: 6819028741\n"
        "Interested persons may contact the Office of Women’s Health at 312-814-4035 for information\n"  # noqa
        "Additional Materials: None"
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 5, 21, 9, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 5, 21, 10, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "il_public_health/201905210900/x/pandas_pans_advisory_council"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[-1]["location"] == {
        "name": "",
        "address": "69 West Washington St., 35th Floor, Chicago, IL"
    }


def test_source():
    assert parsed_items[0]["source"] == "http://www.dph.illinois.gov/events/"


def test_links():
    assert parsed_items[0]["links"] == [{
        'href':
            'http://www.dph.illinois.gov/sites/default/files/events/meeting-agenda/pandas/pans-advisory-council/52119-agenda.pdf',  # noqa
        "title": "Meeting Agenda"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
