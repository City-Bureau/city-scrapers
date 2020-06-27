from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_liquor_control import IlLiquorControlSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_liquor_control.html"),
    url="https://www2.illinois.gov/ilcc/Divisions/Pages/Legal/"
    "Hearing-Schedule-for-Chicago-IL-and-Springfield-IL.aspx",
)

test_response_sample_meeting = file_response(
    join(dirname(__file__), "files", "il_liquor_control_detail.html"),
    url="https://www2.illinois.gov/ilcc/Events/Pages/Board-Meeting-9-18-19.aspx",
)  # Sample meeting page.

spider = IlLiquorControlSpider()

freezer = freeze_time("2019-09-08")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_items_sample_meeting = [
    item for item in spider._next_meeting(test_response_sample_meeting)
]

freezer.stop()


def test_meeting_count():
    assert (
        len(parsed_items) == 4
    )  # Total number of future meeting links contained in main page.


"""
tests for sample meeting page
"""


def test_title():
    assert parsed_items_sample_meeting[0]["title"] == "Board Meeting"


def test_description():
    assert parsed_items_sample_meeting[0]["description"] == ""


def test_start():
    assert parsed_items_sample_meeting[0]["start"] == datetime(2019, 9, 18, 13, 0)


def test_end():
    assert parsed_items_sample_meeting[0]["end"] == datetime(2019, 9, 18, 16, 0)


def test_time_notes():
    assert parsed_items_sample_meeting[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items_sample_meeting[0]["id"]
        == "il_liquor_control/201909181300/x/board_meeting"
    )


def test_status():
    assert parsed_items_sample_meeting[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items_sample_meeting[0]["location"] == {
        "name": "",
        "address": "100 West Randolph 9-040 Chicago, IL",
    }


def test_source():
    assert parsed_items_sample_meeting[0]["source"] == (
        "https://www2.illinois.gov/ilcc/" "Events/Pages/Board-Meeting-9-18-19.aspx"
    )


def test_classification():
    assert parsed_items_sample_meeting[0]["classification"] == BOARD


def test_all_day():
    assert parsed_items_sample_meeting[0]["all_day"] is False
