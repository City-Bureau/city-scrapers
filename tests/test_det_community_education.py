from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, FORUM, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_community_education import DetCommunityEducationSpider

test_response = file_response(
    join(dirname(__file__), "files", "det_community_education.json"),
    url=(
        "https://cecdetroit.org/wp-json/tribe/events/v1/events?start_date=2018-01-01&per_page=100&categories=cec-board-meeting"  # noqa
    )
)
spider = DetCommunityEducationSpider()

freezer = freeze_time("2019-05-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 18


def test_title():
    assert parsed_items[0]["title"
                           ] == "DPN – CEC: School Rating System for Detroit Community Meeting"
    assert parsed_items[-1]["title"] == "Community Education Board Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 10, 25, 17, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0][
        "id"
    ] == "det_community_education/201810251700/x/dpn_cec_school_rating_system_for_detroit_community_meeting"  # noqa


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Detroit Parent Network",
        "address": "726 Lothrop Detroit MI 48202"
    }


def test_source():
    assert parsed_items[0][
        "source"
    ] == "https://cecdetroit.org/event/dpn-cec-school-rating-system-for-detroit-community-meeting/"


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[10]["links"] == [{
        "href":
            "https://cecdetroit.org/wp-content/uploads/2018/12/CEC-Board-Meeting-Agenda-February-2019.pdf",  # noqa
        "title": "CEC Board Meeting Agenda"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == FORUM
    assert parsed_items[-1]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
