from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_pollution_control import IlPollutionControlSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_pollution_control.json"),
    url="https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents",
)
spider = IlPollutionControlSpider()

freezer = freeze_time(datetime(2024, 5, 8, 11, 10))
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_item = parsed_items[0]
freezer.stop()


def test_title():
    assert parsed_item["title"] == "Board Meeting"


def test_description():
    assert (
        parsed_item["description"]
        == "Board Meeting IPCB Office 1021 N Grand Ave E - Room 1244 N (First Floor)Springfield, Illinois- and -MICHAEL A BILANDIC BUILDING160 N. LASALLE - Room N505Chicago, Illinois"  # noqa
    )


def test_start():
    assert parsed_item["start"] == datetime(2023, 5, 18, 11, 0)


def test_end():
    assert parsed_item["end"] == datetime(2023, 5, 18, 11, 0)


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_id():
    assert parsed_item["id"] == "il_pollution_control/202305181100/x/board_meeting"


def test_status():
    assert parsed_item["status"] == PASSED


def test_location():
    assert parsed_item["location"] == {
        "name": "",
        "address": "IPCB Office \n1021 N Grand Ave E - Room 1244 N (First Floor)\nSpringfield, Illinois\n- and -\nMICHAEL A BILANDIC BUILDING\n160 N. LASALLE - Room N505\nChicago, Illinois",  # noqa
    }


def test_source():
    assert parsed_item["source"] == "https://pcb.illinois.gov/ClerksOffice/Calendar"


def test_links():
    assert parsed_item["links"] == [
        {"title": "Agendas", "href": "https://pcb.illinois.gov/CurrentAgendas"},
        {
            "title": "Meeting minutes",
            "href": "https://pcb.illinois.gov/ClerksOffice/MeetingMinutes",
        },
    ]


def test_classification():
    assert parsed_item["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
