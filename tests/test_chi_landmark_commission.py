from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, FORUM, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_landmark_commission import ChiLandmarkCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_landmark_commission.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/landmarks_commission.html",
)
spider = ChiLandmarkCommissionSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2020-08-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 14


def test_title():
    assert parsed_items[0]["title"] == "Commission"
    assert parsed_items[-1]["title"] == "Public Hearing"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 1, 9, 12, 45)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_landmark_commission/202001091245/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == test_response.url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Historic_Preservation/Minutes/CCL_Jan2020_Minutes.pdf",  # noqa
            "title": "Minutes",
        }
    ]
    assert parsed_items[-1]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Historic_Preservation/Publications/CCL_Permit_Hearing_Emergency_Rules_Final_Draft_July_27_2020_RL_final_signed.pdf",  # noqa
            "title": "Public hearing rules",
        },
        {
            "href": "https://livestream.com/accounts/28669066/events/9117952",
            "title": "Live stream link",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Historic_Preservation/Agendas/hearing_form_party_as_right.pdf",  # noqa
            "title": "Appearance Form: Party as a Matter of Right (.pdf)",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Historic_Preservation/Agendas/hearing_form_party_by_request.pdf",  # noqa
            "title": "Appearance Form: Party by Request (.pdf)",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Historic_Preservation/Agendas/hearing_form_interested_person.pdf",  # noqa
            "title": "Appearance Form: Statement of Interested Person",
        },
    ]


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
    assert parsed_items[-1]["classification"] == FORUM
