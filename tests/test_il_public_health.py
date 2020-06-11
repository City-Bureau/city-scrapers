from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.il_public_health import IlPublicHealthSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_public_health.json"),
    url=(
        "http://www.dph.illinois.gov/views/ajax?view_name=events&view_display_id=page&view_args=2019/03&page=0"  # noqa
    ),
)
spider = IlPublicHealthSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2019-09-10")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 10


def test_title():
    assert parsed_items[0]["title"] == "Trauma Advisory Council"


def test_description():
    assert (
        parsed_items[1]["description"]
        == """Downers Grove
VIA VIDEOCONFERENCE AT:
Illinois College of Emergency Physicians, 3000 Woodcreek Dr., Suite #200, Downers Grove, IL
IDPH Bell Building Conference Room, 422 S. 5
th
Street, 3
rd
Floor, Springfield, IL
Illinois Central College (ICC), One College Drive, East Peoria, IL
Unity Point Health-Trinity, 2701 17
th
St., 3
rd
Floor, Rock Island, IL
Memorial Hospital – Belleville, 4550 Memorial Drive, Belleville, IL
Interested persons may contact the Division of EMS and Highway Safety at
217-785-2080
."""  # noqa
    )
    assert (
        parsed_items[-1]["description"]
        == """Rescheduled from February 19, 2019
Meeting has been

CANCELLED

due to lack of Quorum
VIDEO CONFERENCE
525 W. Jefferson St., 4th Floor Video Conference Room, Springfield, IL
69 W. Washington, 35
th
Floor, Director Conf Rm, Chicago, IL
Marion Regional Office, 2309 W. Main St., Marion
245 S. Roosevelt Rd., Bldg 5, W. Chicago
10:00 a.m. – 12:00 p.m.
I
nterested persons may contact Elaine Huddleston in the Office of Health Care Regulations, Division of Health Care Facilities and Programs at
217-782-0483."""  # noqa
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 3, 7, 11, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 3, 7, 12, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_public_health/201903071100/x/trauma_advisory_council"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[-1]["location"] == {
        "name": "",
        "address": "69 W. Washington, 35\nth\nFloor, Director Conf Rm, Chicago, IL",
    }


def test_source():
    assert parsed_items[0]["source"] == "http://www.dph.illinois.gov/events/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://www.dph.illinois.gov/sites/default/files/events/meeting-agenda/trauma-advisory-council/trauma-advisory-council-agenda-3719.pdf",  # noqa
            "title": "Meeting Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
