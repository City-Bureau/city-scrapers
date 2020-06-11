import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, PASSED, TENTATIVE
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_citycouncil import ChiCityCouncilSpider

freezer = freeze_time("2018-12-19")
freezer.start()
with open(join(dirname(__file__), "files", "chi_citycouncil.json"), "r") as f:
    test_response = json.load(f)
spider = ChiCityCouncilSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

parsed_items = [item for item in spider.parse_legistar(test_response)]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "City Council"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 23, 10, 00)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_citycouncil/201901231000/x/city_council"


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[20]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Council Chambers, City Hall",
        "address": "121 N LaSalle St Chicago, IL 60602",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://chicago.legistar.com/DepartmentDetail.aspx?ID=12357&GUID=4B24D5A9-FED0-4015-9154-6BFFFB2A8CB4"  # noqa
    )


def test_links():
    assert parsed_items[20]["links"] == [
        {
            "title": "Agenda",
            "href": "http://media.legistar.com/chic/meetings/937FDFCE-F0EA-452A-B8DF-A0CF51DBD681/Agenda%20Human%20Relations%20N_20181120162153.pdf",  # noqa
        },
        {
            "title": "Summary",
            "href": "http://media.legistar.com/chic/meetings/937FDFCE-F0EA-452A-B8DF-A0CF51DBD681/Corrected%20Summary%20Human%20_20181210125616.pdf",  # noqa
        },
        {
            "href": "http://media.legistar.com/chic/meetings/937FDFCE-F0EA-452A-B8DF-A0CF51DBD681/Human%20Relations%20Notice_20181107153726.pdf",  # noqa
            "title": "Notice",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
