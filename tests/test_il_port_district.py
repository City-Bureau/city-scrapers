from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_port_district import IlPortDistrictSpider

agendas_response = file_response(
    join(dirname(__file__), "files", "il_port_district_agendas.html"),
    url="https://www.iipd.com/calendar/agendas",
)

minutes_response = file_response(
    join(dirname(__file__), "files", "il_port_district_minutes.html"),
    url="https://www.iipd.com/about/board-meeting-minutes",
)

schedules_response = file_response(
    join(dirname(__file__), "files", "il_port_district_schedules.html"),
    url="https://www.iipd.com/calendar/schedules",
)

spider = IlPortDistrictSpider()

freezer = freeze_time("2019-11-22")
freezer.start()

spider.parse_agendas(agendas_response)
spider.parse_minutes(minutes_response)

parsed_items = [item for item in spider.parse_schedules(schedules_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Special Committee Meeting"
    assert parsed_items[1]["title"] == "Special Board Meeting"
    assert parsed_items[3]["title"] == "Board Meeting"
    assert parsed_items[7]["title"] == "Board Meeting"
    assert parsed_items[22]["title"] == "Committee Meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 3, 1, 9, 0)
    assert parsed_items[1]["start"] == datetime(2019, 3, 1, 9, 0)
    assert parsed_items[3]["start"] == datetime(2019, 1, 18, 9, 0)
    assert parsed_items[7]["start"] == datetime(2019, 3, 19, 8, 30)
    assert parsed_items[22]["start"] == datetime(2019, 11, 15, 9, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] is None
    assert parsed_items[3]["end"] is None
    assert parsed_items[7]["end"] is None
    assert parsed_items[22]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_port_district/201903010900/x/special_committee_meeting"
    )
    assert (
        parsed_items[1]["id"] == "il_port_district/201903010900/x/special_board_meeting"
    )
    assert parsed_items[3]["id"] == "il_port_district/201901180900/x/board_meeting"
    assert parsed_items[7]["id"] == "il_port_district/201903190830/x/board_meeting"
    assert parsed_items[22]["id"] == "il_port_district/201911150900/x/committee_meeting"


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[1]["status"] == PASSED
    assert parsed_items[3]["status"] == PASSED
    assert parsed_items[7]["status"] == PASSED
    assert parsed_items[22]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "3600 E. 95th St. Chicago, IL 60617",
        "name": "Illinois International Port District ",
    }

    assert parsed_items[1]["location"] == {
        "address": "3600 E. 95th St. Chicago, IL 60617",
        "name": "Illinois International Port District ",
    }

    assert parsed_items[3]["location"] == {
        "address": "3600 E. 95th St. Chicago, IL 60617",
        "name": "Illinois International Port District ",
    }

    assert parsed_items[7]["location"] == {
        "address": "3600 E. 95th St. Chicago, IL 60617",
        "name": "Illinois International Port District ",
    }

    assert parsed_items[22]["location"] == {
        "address": "3600 E. 95th St. Chicago, IL 60617",
        "name": "Illinois International Port District ",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.iipd.com/calendar/schedules"
    assert parsed_items[1]["source"] == "https://www.iipd.com/calendar/schedules"
    assert parsed_items[3]["source"] == "https://www.iipd.com/calendar/schedules"
    assert parsed_items[7]["source"] == "https://www.iipd.com/calendar/schedules"
    assert parsed_items[22]["source"] == "https://www.iipd.com/calendar/schedules"


def test_links():
    # Spider returns https links, but test file sees them as http
    assert parsed_items[0]["links"] == []

    assert parsed_items[1]["links"][0] == {
        "href": "http://www.iipd.com/sites/default/files/documents/Bd%20Meeting%20Minutes%20_%20Special%20Bd%20Meeting_3-1-19.pdf",  # noqa
        "title": "Board Meeting Minutes",
    }

    assert parsed_items[3]["links"][0] == {
        "href": "http://www.iipd.com/sites/default/files/documents/Bd%20Meeting%20Minutes%201-18-19.pdf",  # noqa
        "title": "Board Meeting Minutes",
    }

    assert parsed_items[7]["links"][0] == {
        "href": "http://www.iipd.com/sites/default/files/documents/Bd%20Meeting%20Minutes%203-19-19.pdf",  # noqa
        "title": "Board Meeting Minutes",
    }

    assert parsed_items[22]["links"][0] == {
        "href": "http://www.iipd.com/sites/default/files/documents/L%26A%20Agenda%20November%202019.pdf",  # noqa
        "title": "Leases and Agreement Committee Agenda November 2019",
    }

    assert parsed_items[22]["links"][1] == {
        "href": "http://www.iipd.com/sites/default/files/documents/F%26P%20Agenda%20November%202019.pdf",  # noqa
        "title": "Finance and Personnel Committee Agenda November 2019",
    }


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[1]["classification"] == BOARD
    assert parsed_items[3]["classification"] == BOARD
    assert parsed_items[7]["classification"] == BOARD
    assert parsed_items[22]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
