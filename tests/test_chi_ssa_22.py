from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_ssa_22 import ChiSsa22Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_22.html"),
    url="http://www.andersonville.org/our-organizations/andersonville-ssa-22/",
)

spider = ChiSsa22Spider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2020-05-12")
freezer.start()

parsed_items = sorted([item for item in spider.parse(test_response)],
                      key=lambda i: i["start"],
                      reverse=True)

freezer.stop()


def test_count():
    assert len(parsed_items) == 11


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Commission"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == 'All meetings are held at the Andersonville' \
                                  ' Chamber of Commerce conference room'


def test_start():
    expected_starts = [
        datetime(2020, 11, 10, 9, 30),
        datetime(2020, 9, 8, 9, 30),
        datetime(2020, 7, 7, 9, 30),
        datetime(2020, 5, 7, 9, 30),
        datetime(2020, 4, 7, 9, 30),
        datetime(2020, 3, 10, 9, 30),
        datetime(2020, 1, 28, 9, 30),
        datetime(2019, 11, 12, 9, 30),
        datetime(2019, 9, 10, 9, 30),
        datetime(2019, 7, 9, 9, 30),
        datetime(2019, 5, 21, 9, 30)
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["start"] == expected_starts[i]


"""
def test_end():
    expected_ends = [
        datetime(2020, 11, 10, 11, 30),
        datetime(2020, 9, 8, 11, 30),
        datetime(2020, 7, 7, 11, 30),
        datetime(2020, 5, 7, 11, 30),
        datetime(2020, 4, 7, 11, 30),
        datetime(2020, 3, 10, 11, 30),
        datetime(2020, 1, 28, 11, 30),
        datetime(2019, 11, 12, 11, 30),
        datetime(2019, 9, 10, 11, 30),
        datetime(2019, 7, 9, 11, 30),
        datetime(2019, 5, 21, 11, 30)
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["end"] == expected_ends[i]
"""


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == '9:30am or 3:45pm ' \
                                 '(Please check our Monthly Newsletter for more information)'


def test_id():
    expected_ids = [
        'chi_ssa_22/202011100930/x/commission', 'chi_ssa_22/202009080930/x/commission',
        'chi_ssa_22/202007070930/x/commission', 'chi_ssa_22/202005070930/x/commission',
        'chi_ssa_22/202004070930/x/commission', 'chi_ssa_22/202003100930/x/commission',
        'chi_ssa_22/202001280930/x/commission', 'chi_ssa_22/201911120930/x/commission',
        'chi_ssa_22/201909100930/x/commission', 'chi_ssa_22/201907090930/x/commission',
        'chi_ssa_22/201905210930/x/commission'
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["id"] == expected_ids[i]


def test_status():
    expected_status = [
        TENTATIVE, TENTATIVE, TENTATIVE, PASSED, PASSED, PASSED, PASSED, PASSED, PASSED, PASSED,
        PASSED, PASSED
    ]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["status"] == expected_status[i]


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "Andersonville Chamber of Commerce",
        "address": "5153 N. Clark St. #228 Chicago, Illinois 60640"
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
