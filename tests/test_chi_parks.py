from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, CANCELLED, FORUM, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.http import HtmlResponse
from scrapy.settings import Settings

from city_scrapers.spiders.chi_parks import ChiParksSpider

CALENDAR_URL = "https://chicagoparkdistrict.legistar.com/Calendar.aspx"
ADMIN_BUILDING = {
    "name": "Chicago Park District Administration Building",
    "address": "4830 South Western Avenue, Chicago, IL 60609",
}

# The calendar table as Legistar now renders it: the iCal column's header holds
# hidden sort buttons whose value is a single space
TABLE_SNIPPET = """
<table class="rgMasterTable">
  <thead><tr>
    <th class="rgHeader">Name</th>
    <th class="rgHeader">Meeting Date</th>
    <th class="rgHeader"><img title="Export to Calendar" src="Images/ical.gif"
      alt="Export to Calendar"><input type="button" value=" " class="rgSortAsc"><input
      type="button" value=" " class="rgSortDesc"></th>
    <th class="rgHeader">Meeting Time</th>
    <th class="rgHeader">Meeting Location</th>
  </tr></thead>
  <tbody><tr class="rgRow">
    <td>Board of Commissioners</td>
    <td>12/9/2026</td>
    <td><a href="View.ashx?M=IC&amp;ID=1&amp;GUID=A"><img
      alt="Export to iCalendar"></a></td>
    <td>9:00 AM</td>
    <td>REGULAR BOARD MEETING<br>Chicago Park District Administration Building<br>
      4830 South Western Avenue, Chicago, IL 60609</td>
  </tr></tbody>
</table>
"""


def _parse(archive):
    spider = ChiParksSpider()
    spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": archive})
    response = file_response(
        join(dirname(__file__), "files", "chi_parks.html"), url=CALENDAR_URL
    )
    with freeze_time("2026-11-02"):
        return list(spider.parse_legistar(spider._parse_legistar_events(response)))


@pytest.fixture(scope="module")
def parsed_items():
    return _parse(archive=False)


@pytest.fixture(scope="module")
def archive_items():
    return _parse(archive=True)


@pytest.fixture(scope="module")
def spider():
    spider = ChiParksSpider()
    spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": True})
    return spider


def test_count(parsed_items):
    assert len(parsed_items) == 21


def test_archive_count(archive_items):
    assert len(archive_items) == 21


def test_one_year_lookback():
    spider = ChiParksSpider()
    spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})
    events = [
        {
            "Name": "Board of Commissioners",
            "Meeting Date": date,
            "Meeting Time": "9:00 AM",
        }
        for date in ["11/3/2025", "11/1/2025"]
    ]
    with freeze_time("2026-11-02"):
        items = list(spider.parse_legistar(events))
    assert [item["start"] for item in items] == [datetime(2025, 11, 3, 9, 0)]


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Board of Commissioners"
    assert parsed_items[2]["title"] == "Board of Commissioners: Public Hearing"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""
    assert (
        parsed_items[4]["description"]
        == "Microsoft Teams Meeting link: https://teams.microsoft.com/meet/281416815467649?p=ZBGUh7bABKSuDpFFeT"  # noqa
    )


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 12, 9, 9, 0)
    assert parsed_items[-1]["start"] == datetime(2026, 1, 21, 9, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == "Estimated 2 hour duration"


def test_id(parsed_items):
    assert parsed_items[0]["id"] == "chi_parks/202612090900/x/board_of_commissioners"


def test_status(parsed_items):
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[6]["status"] == PASSED
    assert parsed_items[7]["status"] == CANCELLED


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[2]["classification"] == FORUM
    assert parsed_items[4]["classification"] == FORUM


def test_location(parsed_items):
    assert parsed_items[0]["location"] == ADMIN_BUILDING
    assert parsed_items[3]["location"] == {
        "name": "ComEd Recreation Center Addams (Jane)",
        "address": "1434 South Loomis Street, Chicago, IL 60608",
    }
    assert parsed_items[4]["location"] == {"name": "Virtual", "address": ""}
    assert parsed_items[7]["location"] == {"name": "TBD", "address": ""}


def test_links(parsed_items):
    assert parsed_items[0]["links"] == []
    assert parsed_items[6]["links"] == [
        {
            "href": "https://chicagoparkdistrict.legistar.com/View.ashx?M=A&ID=1366782&GUID=E53AF85C-F11F-44AF-8F4B-BD9412E8A99B",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://chicagoparkdistrict.legistar.com/View.ashx?M=M&ID=1366782&GUID=E53AF85C-F11F-44AF-8F4B-BD9412E8A99B",  # noqa
            "title": "Minutes",
        },
    ]


def test_source(parsed_items):
    assert parsed_items[0]["source"] == CALENDAR_URL
    assert (
        parsed_items[6]["source"]
        == "https://chicagoparkdistrict.legistar.com/MeetingDetail.aspx?ID=1366782&GUID=E53AF85C-F11F-44AF-8F4B-BD9412E8A99B&Options=info|&Search="  # noqa
    )


def test_all_day(archive_items):
    for item in archive_items:
        assert item["all_day"] is False


def test_ical_column_with_blank_sort_buttons(spider):
    response = HtmlResponse(url=CALENDAR_URL, body=TABLE_SNIPPET, encoding="utf-8")
    events = spider._parse_legistar_events(response)
    assert len(events) == 1
    assert events[0]["iCalendar"] == {
        "url": "https://chicagoparkdistrict.legistar.com/View.ashx?M=IC&ID=1&GUID=A"
    }
    assert events[0]["Meeting Date"] == "12/9/2026"


def test_missing_table_logs_warning(spider, caplog):
    """
    caplog is a built-in pytest fixture that captures log records. A page with no
    events table must log a warning instead of finishing silently with no meetings.
    """
    response = HtmlResponse(
        url=CALENDAR_URL, body="<html><body></body></html>", encoding="utf-8"
    )
    assert list(spider.parse_legistar(spider._parse_legistar_events(response))) == []
    assert "No Legistar events table found" in caplog.text
    assert "No Legistar events to parse" in caplog.text


@pytest.mark.parametrize(
    "location_text,expected",
    [
        (
            "REGULAR BOARD MEETING Austin Town Hall Park 5610 West Lake Street Chicago, IL 60644",  # noqa
            {
                "name": "Austin Town Hall Park",
                "address": "5610 West Lake Street, Chicago, IL 60644",
            },
        ),
        (
            "REGULAR BOARD MEETING Sherman Park 1301 West 52nd Street Chicago, IL, 60609",  # noqa
            {
                "name": "Sherman Park",
                "address": "1301 West 52nd Street, Chicago, IL 60609",
            },
        ),
        (
            "Chicago Park District Administration Building 4830 South Western Avenue, Chicago, IL 60609 PUBLIC HEARING",  # noqa
            ADMIN_BUILDING,
        ),
        (
            "SPECIAL MEETING Chicago Park District Administration Building (Park 596) 4830 S. Western Avenue, Chicago, IL 60609",  # noqa
            ADMIN_BUILDING,
        ),
        (
            "SPECIAL BOARD MEETING Administration Building 4830 South Western Avenue, Chicago IL 60609",  # noqa
            ADMIN_BUILDING,
        ),
        (
            "PUBLIC BUDGET FORUM (VIRTUAL) Online meeting link: https://tinyurl.com/CPKDFY26FORUM",  # noqa
            {"name": "Virtual", "address": ""},
        ),
        (
            "Microsoft Teams Meeting link: https://teams.microsoft.com/meet/1",
            {"name": "Virtual", "address": ""},
        ),
        ("THIS MEETING HAS BEEN CANCELLED", {"name": "TBD", "address": ""}),
    ],
)
def test_location_formats(spider, location_text, expected):
    assert spider._parse_location(location_text) == expected


@pytest.mark.parametrize(
    "location,expected",
    [
        (
            "PUBLIC BUDGET FORUM (VIRTUAL) Online meeting link: https://tinyurl.com/CPKDFY26FORUM",  # noqa
            "Online meeting link: https://tinyurl.com/CPKDFY26FORUM",
        ),
        (
            {
                "label": "PUBLIC BUDGET FORUM (VIRTUAL) Join on Teams",
                "url": "https://teams.microsoft.com/meet/1",
            },
            "Join on Teams https://teams.microsoft.com/meet/1",
        ),
        (
            "PUBLIC BUDGET FORUM Chicago Park District Administration Building 4830 South Western Avenue, Chicago, IL 60609 or join online: https://tinyurl.com/x",  # noqa
            "or join online: https://tinyurl.com/x",
        ),
        (
            "REGULAR BOARD MEETING Sherman Park 1301 West 52nd Street Chicago, IL, 60609",  # noqa
            "",
        ),
    ],
)
def test_virtual_meeting_description(spider, location, expected):
    item = {"Meeting Location": location}
    location_text = spider._parse_location_text(item)
    assert spider._parse_description(item, location_text) == expected


def test_missing_time_uses_midnight_with_note(spider, caplog):
    event = {"Name": "Board of Commissioners", "Meeting Date": "12/9/2026"}
    with freeze_time("2026-11-02"):
        item = next(spider.parse_legistar([event]))
    assert item["start"] == datetime(2026, 12, 9, 0, 0)
    assert (
        item["time_notes"]
        == "Please check the meeting attachment for start time details."
    )
    assert "Unreadable time" in caplog.text


def test_unreadable_date_is_skipped_with_warning(spider, caplog):
    event = {
        "Name": "Board of Commissioners",
        "Meeting Date": "12/39/2026",
        "Meeting Time": "9:00 AM",
    }
    with freeze_time("2026-11-02"):
        assert list(spider.parse_legistar([event])) == []
    assert "Skipping meeting with unreadable date" in caplog.text


def test_rescheduled_meeting_is_not_cancelled(spider):
    event = {
        "Name": "Board of Commissioners",
        "Meeting Date": "7/16/2025",
        "Meeting Time": "8:00 AM",
        "Meeting Location": "RESCHEDULED REGULAR BOARD MEETING Chicago Park District Administration Building 4830 South Western Avenue, Chicago, IL 60609",  # noqa
    }
    with freeze_time("2026-11-02"):
        item = next(spider.parse_legistar([event]))
    assert item["status"] == PASSED
    assert item["location"] == ADMIN_BUILDING


def test_rescheduled_virtual_meeting_is_not_cancelled(spider):
    event = {
        "Name": "Budget Forum",
        "Meeting Date": "9/17/2026",
        "Meeting Time": "6:00 PM",
        "Meeting Location": "PUBLIC BUDGET FORUM (VIRTUAL) Rescheduled from 9/10. Microsoft Teams Meeting link: https://teams.microsoft.com/meet/1",  # noqa
    }
    with freeze_time("2026-11-02"):
        item = next(spider.parse_legistar([event]))
    assert item["status"] == PASSED
    assert item["description"].startswith("Rescheduled from 9/10.")
