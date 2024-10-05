from datetime import datetime
from os.path import dirname, join
from city_scrapers_core.constants import BOARD, PASSED
import pytest
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_northeastern_il_university import ChiNortheasternIlUniversitySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_northeastern_il_university.html"),
    url="https://www.neiu.edu/about/board-of-trustees/board-meeting-materials",
)
spider = ChiNortheasternIlUniversitySpider()

freezer = freeze_time("2024-10-04")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "BOARD MEETING"
    assert parsed_items[1]["title"] == "FINANCE, BUILDINGS AND GROUNDS COMMITTEE MEETING"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 9, 19, 13, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2024, 9, 19, 15, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_northeastern_il_university/202409191300/x/board_meeting"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Student Union – Alumni Hall",
        "address": "5500 N. St. Louis Avenue, Chicago, IL 60625"
    }
    assert parsed_items[3]["location"] == {
        "name": "Student Union Room 214",
        "address": "5500 N. St. Louis Avenue, Chicago, IL 60625"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.neiu.edu/about/board-of-trustees/board-meeting-materials"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.neiu.edu/sites/default/files/2024-09/2024.09.19.%20Agenda_FINAL.pdf",
            "title": "Meeting Agenda"
        },
        {
            "href": "https://www.neiu.edu/sites/default/files/2024-09/2024.09.19.%20President%27s%20Report_combined.pdf",
            "title": "President's Report to the Board"
        },
        {
            "href": "https://www.neiu.edu/sites/default/files/2024-09/Colorblind%20image_Page_3_0.jpg",
            "title": "Markham Prairie Image - colorblind friendly"
        },
        {
            "href": "https://youtu.be/8PLfgYgandQ",
            "title": "Meeting Video"
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
