from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_sports_facilities_authority import IlSportsFacilitiesAuthoritySpider

test_response = file_response(
    join(dirname(__file__), "files", "il_sports_facilities_authority.html"),
    url="https://www.isfauthority.com/governance/board-meetings/",
)
spider = IlSportsFacilitiesAuthoritySpider()

freezer = freeze_time("2019-10-21")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_title():
    assert parsed_items[1]["title"] == "Board Meeting"


def test_start():
    assert parsed_items[1]["start"] == datetime(2019, 9, 19, 10, 0)


def test_location():
    assert parsed_items[1]["location"] == {
        "name": "Authority offices",
        "address": "Guaranteed Rate Field, 333 West 35th Street, Chicago, IL"
    }


def test_source():
    assert parsed_items[1]["source"] == "https://www.isfauthority.com/governance/board-meetings/"


def test_links():
    assert parsed_items[1]["links"] == [{
        'href': (
            'https://236c3m49r38mg7ixa39zqru1-wpengine.netdna-ssl.com/'
            'wp-content/uploads/2019/09/ISFA-Board-Meeting-Agenda-9-2019.pdf'
        ),
        'title': 'Agenda'
    }]


def test_classification():
    assert parsed_items[1]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
