from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, CANCELLED, FORUM, NOT_CLASSIFIED, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_pollution_control import IlPollutionControlSpider

test_minutes_response = file_response(
    join(dirname(__file__), "files", "il_pollution_control.html"),
    url="https://pcb.illinois.gov/ClerksOffice/MeetingMinutes",
)

test_response = file_response(
    join(dirname(__file__), "files", "il_pollution_control.json"),
    url="https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents",
)
spider = IlPollutionControlSpider()

freezer = freeze_time("2019-10-03")
freezer.start()

parsed_items = [item for item in spider._parse_json(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 30


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Board Meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 5, 23, 11, 0)


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] is None


def test_id():
    assert parsed_items[0]["id"] == 'il_pollution_control/201905231100/x/board_meeting'


def test_status():
    expected_counts = {CANCELLED: 2, PASSED: 22, TENTATIVE: 6}
    actual_counts = {}
    for key in expected_counts:
        actual_counts[key] = len([item for item in parsed_items if item['status'] == key])
        assert actual_counts[key] == expected_counts[key]


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"]["name"] == "Chicago IPCB Office"


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == "https://pcb.illinois.gov/ClerksOffice/Calendar"


def test_links():
    # Must use `list()` so generator is fully consumed and spider.link_map is populated.
    list(spider._parse_minutes(test_minutes_response))
    expected_links = {
        datetime(2019, 1, 17).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-99687/1-17-2019 draft2.pdf",  # noqa
        datetime(2019, 2, 28).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-99956/2-28-2019 draft2.pdf",  # noqa
        datetime(2019, 3, 14).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-99970/3-14-2019 draft2.pdf",  # noqa
        datetime(2019, 3, 28).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-100053/3-28-2019 draft2.pdf",  # noqa
        datetime(2019, 2, 14).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-99955/2-14-2019 draft2.pdf",  # noqa
        datetime(2019, 4, 11).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-100602/04-11-2019 draft1.pdf",  # noqa
        datetime(2019, 4, 25).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-100603/04-25-2019 draft1.pdf",  # noqa
        datetime(2019, 5, 30).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-100725/05-30-2019 draft1.pdf",  # noqa
        datetime(2019, 6, 20).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-100854/06-20-2019 draft1.pdf",  # noqa
        datetime(2019, 7, 25).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-100956/07-25-2019 draft1.pdf",  # noqa
        datetime(2019, 8, 22).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-101165/08-22-2019 draft1.pdf",  # noqa
        datetime(2019, 9, 19).date():
            "https://pcb.illinois.gov/documents/dsweb/Get/Document-101211/09-19-2019 draft1.pdf",  # noqa
    }

    for dt in expected_links:
        assert expected_links[dt] == spider.link_map[dt]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
