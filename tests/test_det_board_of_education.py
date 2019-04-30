from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from freezegun import freeze_time
from scrapy.http import TextResponse

from city_scrapers.spiders.det_board_of_education import DetBoardOfEducationSpider

with open(join(dirname(__file__), "files", "det_board_of_education.ics"), "rb") as f:
    body = f.read()

test_response = TextResponse(
    url="https://www.detroitk12.org/site/handlers/icalfeed.ashx?MIID=14864",
    body=body,
    encoding="utf-8"
)
spider = DetBoardOfEducationSpider()

freezer = freeze_time("2019-04-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 33


def test_title():
    assert parsed_items[0]["title"] == "DPSCD Regular Board Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 4, 16, 17, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 4, 16, 19, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"
                           ] == "det_board_of_education/201904161730/x/dpscd_regular_board_meeting"


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[-1]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "Renaissance High School, Detroit, MI 48235, USA"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.detroitk12.org/Page/9425"


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_all_day():
    assert parsed_items[0]["all_day"] is False
