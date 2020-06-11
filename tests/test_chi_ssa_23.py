from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_ssa_23 import ChiSsa23Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_23.html"),
    url="https://www.lincolnparkchamber.com/clark-street-ssa-administration/",
)

spider = ChiSsa23Spider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2020-05-11")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)],
    key=lambda i: i["start"],
    reverse=True,
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 12


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Commission"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert (
        item["description"] == "All meetings held Wednesdays at 4:00 p.m.  "
        "Meetings typically run 90 minute"
        "s. Please contact the LPCC to confirm meeting "
        "locations (773) 880-5200. "
    )


def test_start():
    expected_starts = [
        datetime(2020, 11, 18, 16, 0),
        datetime(2020, 9, 9, 16, 0),
        datetime(2020, 7, 8, 16, 0),
        datetime(2020, 5, 27, 16, 0),
        datetime(2020, 4, 22, 16, 0),
        datetime(2020, 4, 3, 10, 30),
        datetime(2020, 3, 24, 9, 37),
        datetime(2020, 2, 5, 16, 0),
        datetime(2019, 11, 13, 16, 0),
        datetime(2019, 9, 4, 16, 0),
        datetime(2019, 7, 10, 16, 0),
        datetime(2019, 5, 15, 16, 0),
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["start"] == expected_starts[i]


def test_end():
    expected_ends = [
        datetime(2020, 11, 18, 17, 30),
        datetime(2020, 9, 9, 17, 30),
        datetime(2020, 7, 8, 17, 30),
        datetime(2020, 5, 27, 17, 30),
        datetime(2020, 4, 22, 17, 30),
        datetime(2020, 4, 3, 12, 00),
        datetime(2020, 3, 24, 11, 7),
        datetime(2020, 2, 5, 17, 30),
        datetime(2019, 11, 13, 17, 30),
        datetime(2019, 9, 4, 17, 30),
        datetime(2019, 7, 10, 17, 30),
        datetime(2019, 5, 15, 17, 30),
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["end"] == expected_ends[i]


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == "Estimated 90 minutes duration"


def test_id():
    expected_ids = [
        "chi_ssa_23/202011181600/x/commission",
        "chi_ssa_23/202009091600/x/commission",
        "chi_ssa_23/202007081600/x/commission",
        "chi_ssa_23/202005271600/x/commission",
        "chi_ssa_23/202004221600/x/commission",
        "chi_ssa_23/202004031030/x/commission",
        "chi_ssa_23/202003240937/x/commission",
        "chi_ssa_23/202002051600/x/commission",
        "chi_ssa_23/201911131600/x/commission",
        "chi_ssa_23/201909041600/x/commission",
        "chi_ssa_23/201907101600/x/commission",
        "chi_ssa_23/201905151600/x/commission",
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["id"] == expected_ids[i]


def test_status():
    expected_status = [
        TENTATIVE,
        TENTATIVE,
        TENTATIVE,
        TENTATIVE,
        PASSED,
        PASSED,
        PASSED,
        PASSED,
        PASSED,
        PASSED,
        PASSED,
        PASSED,
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["status"] == expected_status[i]


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "Lincoln Park Chamber of Commerce",
        "address": "2468 N. Lincoln Chicago, IL 60614",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == test_response.url


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION


def test_all_day():
    for i in range(len(parsed_items)):
        assert parsed_items[i]["all_day"] is False
