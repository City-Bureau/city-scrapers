from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMISSION,
    COMMITTEE,
    TENTATIVE,
)
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_criminal_justice_information import (
    IlCriminalJusticeInformationSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "il_criminal_justice_information.json"),
    url="https://agency.icjia-api.cloud/graphql",
)
spider = IlCriminalJusticeInformationSpider()

freezer = freeze_time("2024-07-16")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 19


def test_title():
    assert (
        parsed_items[0]["title"]
        == "TRAFFIC & PEDESTRIAN STOP STATISTICAL STUDY TASK FORCE: July 25, 2024"  # noqa
    )


def test_description():
    assert (
        parsed_items[0]["description"]
        == "Thursday, July 25, 2024\n11:30pm – 12:30pm\nLocation\nVia WebEx Video Conference/Teleconference"  # noqa
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 7, 25, 11, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2024, 7, 25, 12, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_criminal_justice_information/202407251130/x/traffic_pedestrian_stop_statistical_study_task_force_july_25_2024"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "TBD",
        "address": "",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://icjia.illinois.gov/news/meetings/traffic-and-pedestrian-stop-statistical-study-task-force-july-25-2024/"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://agency.icjia-api.cloud/uploads/Traffic_Data_Stop_Task_Force_Agenda_07_24_24_KA_TL_df57bde328.pdf",  # noqa
            "title": "Traffic Data Stop Task Force Agenda 07-24-24 KA TL",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Budget Committee Meeting August 27, 2026", COMMITTEE),
        ("Authority Board Meeting: October 8, 2026", BOARD),
        (
            "STATE CRISIS INTERVENTION PROGRAM ADVISORY COMMITTEE: Sep 28, 2023",
            ADVISORY_COMMITTEE,
        ),
        ("Clean Slate Task Force: August 26, 2026", COMMISSION),
    ],
)
def test_parse_classification(title, expected):
    assert spider._parse_classification(title) == expected


def test_all_day():
    assert parsed_items[0]["all_day"] is False


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Budget Committee Agenda 082726.pdf", "Budget Committee Agenda"),
        (
            "ICJIA Authority Board Agenda - 10.08.2026.pdf",
            "ICJIA Authority Board Agenda",
        ),
        (
            "ICJIA Violence Prevention Ad Hoc Committee Agenda 8-13-26.pdf",
            "ICJIA Violence Prevention Ad Hoc Committee Agenda",
        ),
        (
            "Missing and Murdered Task Force Agenda 7.13.2026.pdf",
            "Missing and Murdered Task Force Agenda",
        ),
    ],
)
def test_parse_link_title(name, expected):
    assert spider._parse_link_title(name) == expected


def test_location_multiple_locations():
    # Budget Committee lists Chicago and Springfield; the first is the location
    assert parsed_items[2]["location"] == {
        "name": "Michael A. Bilandic Building",
        "address": "160 N. LaSalle Street, Room N-502, Chicago, Illinois, 60661",
    }
    assert "Michael A. Bilandic Building" in parsed_items[2]["description"]
    assert "524 South 2nd Street, Suite 220" in parsed_items[2]["description"]


def test_location_city_line():
    assert parsed_items[6]["location"] == {
        "name": "",
        "address": "160 N La Salle St Room: N505, Chicago, IL",
    }


def test_location_single_line():
    assert parsed_items[16]["location"] == {
        "name": "Cook County Medical Examiner’s Office",
        "address": "2121 W. Harrison, Chicago, IL",
    }


def test_online_meeting_uses_fuller_body():
    # The summary is cut short; the body has the location and the WebEx link
    description, location = spider._parse_description_and_location(
        {
            "summary": "Public meeting on 10/13/26 at 1:00 PM CST via Webex.",
            "body": (
                "Public meeting on 10/13/26 at 1:00 PM CST via Webex.\n\n"
                "Location: WebEx Meeting Link https://illinois.webex.com/j.php?MTID=m1\n"  # noqa
            ),
        }
    )
    assert location == {"name": "TBD", "address": ""}
    assert description == (
        "Public meeting on 10/13/26 at 1:00 PM CST via Webex.\n\n"
        "Location: WebEx Meeting Link https://illinois.webex.com/j.php?MTID=m1"
    )


def test_online_meeting_link_added_to_description():
    # The link is only in the shorter body, so it's added to the description
    description, location = spider._parse_description_and_location(
        {
            "summary": "Public meeting on 5/12/2026, at 1:00 pm by Webex. All are invited.",  # noqa
            "body": "Link: https://illinois.webex.com/j.php?MTID=m1",
        }
    )
    assert location == {"name": "TBD", "address": ""}
    assert description == (
        "Public meeting on 5/12/2026, at 1:00 pm by Webex. All are invited.\n\n"
        "Meeting link: https://illinois.webex.com/j.php?MTID=m1"
    )


def test_location_from_body_when_summary_is_cut_short():
    # Authority Board, Oct 8 2026: the summary has no location, the body does
    description, location = spider._parse_description_and_location(
        {
            "summary": "Authority Board Meeting Thursday, October 8, 2026\n10:00 a.m. to 11:00 a.m.\n\n",  # noqa
            "body": (
                "Authority Board Meeting Thursday, October 8, 2026\n\n"
                "10:00 a.m. to 11:00 a.m.\n \n"
                "Illinois Criminal Justice Information Authority\n\n\n"
                "Location:\nVia Webex Video Conference/Teleconference\n\n"
                "Chicago: Michael Bilandic Building, 160 N. LaSalle Street, Room N505\n\n"  # noqa
                "Springfield: ICJIA Office, 524 S. 2nd Street, Suite 220\n"
            ),
        }
    )
    assert location == {
        "name": "Michael Bilandic Building",
        "address": "160 N. LaSalle Street, Room N505, Chicago, IL",
    }
    assert "Chicago: Michael Bilandic Building" in description
    assert "Springfield: ICJIA Office, 524 S. 2nd Street, Suite 220" in description
