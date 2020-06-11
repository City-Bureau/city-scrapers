from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_schools import ChiSchoolsSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_schools.html"),
    url="https://www.cpsboe.org/meetings/details/279",
)
test_calendar_response = file_response(
    join(dirname(__file__), "files", "chi_schools_cal.html"),
    url="https://www.cpsboe.org/meetings/planning-calendar",
)

spider = ChiSchoolsSpider()
spider.meeting_dates = []

freezer = freeze_time("2019-10-23")
freezer.start()

parsed_item = [item for item in spider._parse_detail(test_response)][0]
parsed_items = [item for item in spider._parse_calendar(test_calendar_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 14


def test_id():
    assert parsed_item["id"] == "chi_schools/201911201030/x/board_of_education"


def test_links():
    assert parsed_item["links"] == []


def test_title():
    assert parsed_item["title"] == "Board of Education"


def test_source():
    assert parsed_item["source"] == test_response.url


def test_description():
    assert (
        parsed_item["description"]
        == """For the November 20, 2019 Board Meeting, advance registration to speak and observe will be available beginning Monday, November 18th at 10:30 a.m. and close Tuesday, November 19th at 5:00 p.m., or until all slots are filled. You can advance register during the registration period by the following methods:
Online: www.cpsboe.org (recommended)
Phone: (773) 553-1600
In Person: 1 North Dearborn Street, Suite 950

To ensure equity of access to address the Board, an individual may not speak at two (2) consecutive Board Meetings. In the event an individual registers to speak at a consecutive Board Meeting, the individual will not be called to address the Board.
Although Advance Registration is recommended, you can also register to observe a meeting on the day of a Board Meeting via:

Same Day In Person Observer Registration: 42 W. Madison Street lobby
Registration Time: Opens at 10:15 AM and will remain open for the duration of the Board Meeting

Same Day, In-Person Observer Registrations are taken on a first come, first serve basis as seats become available.
The Public Participation segment of the meeting will begin as indicated in the meeting agenda and proceed for no more than 60 registered speakers for the two hours."""  # noqa
    )
    assert parsed_items[0]["description"] == ""


def test_classification():
    assert parsed_item["classification"] == BOARD


def test_start():
    assert parsed_item["start"] == datetime(2019, 11, 20, 10, 30)


def test_end():
    assert parsed_item["end"] is None


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_status():
    assert parsed_item["status"] == TENTATIVE


def test_all_day():
    assert parsed_item["all_day"] is False


def test_location():
    assert parsed_item["location"] == spider.location
