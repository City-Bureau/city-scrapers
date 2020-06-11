from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_landmark_commission import ChiLandmarkCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_landmark_commission.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/landmarks_commission.html",
)
spider = ChiLandmarkCommissionSpider()

freezer = freeze_time("2019-10-07")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 28


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 10, 12, 45)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_landmark_commission/201901101245/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == test_response.url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Historic_Preservation/Minutes/CCL_Jan2019_Minutes.pdf",  # noqa
            "title": "Minutes",
        }
    ]
    assert parsed_items[13]["links"] == [
        {
            "title": "Public Hearing Notice",
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Historic_Preservation/Agendas/Nuveen_House_Public_Hearing_Legal_Notice_16OCT_2019.pdf",  # noqa
        }
    ]


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
