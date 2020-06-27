from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_commerce import IlCommerceSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_commerce.html"),
    url="https://www.icc.illinois.gov/meetings/default.aspx?dts=32&et=1&et=5&et=3",
)
test_detail_response = file_response(
    join(dirname(__file__), "files", "il_commerce_detail.html"),
    url="https://www.icc.illinois.gov/meetings/policy-session/meeting/21353",
)
spider = IlCommerceSpider()

freezer = freeze_time("2020-03-05")
freezer.start()

parsed_requests = [item for item in spider.parse(test_response)]
parsed_item = [item for item in spider._parse_detail(test_detail_response)][0]

freezer.stop()


def test_count():
    assert len(parsed_requests) == 6


def test_title():
    assert parsed_item["title"] == "Policy Session Summer Preparedness Policy Session"


def test_description():
    assert parsed_item["description"] == ""


def test_start():
    assert parsed_item["start"] == datetime(2020, 5, 27, 11, 30)


def test_end():
    assert parsed_item["end"] is None


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_id():
    assert (
        parsed_item["id"]
        == "il_commerce/202005271130/x/policy_session_summer_preparedness_policy_session"  # noqa
    )


def test_status():
    assert parsed_item["status"] == TENTATIVE


def test_location():
    assert parsed_item["location"] == {
        "name": "Eighth Floor, State of Illinois Building",
        "address": "160 North LaSalle Street Chicago, Illinois 60601",
    }


def test_source():
    assert parsed_item["source"] == test_detail_response.url


def test_links():
    assert parsed_item["links"] == [
        {
            "href": "https://www.icc.illinois.gov/downloads/public/letter/21690.pdf",
            "title": "Public Utility Cover Letter",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/agenda/21690.pdf",
            "title": "Policy Agenda",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/Ameren-Summer2020.pdf",  # noqa
            "title": "Ameren",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/ComEd_summer2020.pdf",  # noqa
            "title": "ComEd",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/CUB_summer2020.pdf",
            "title": "CUB",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/AG.pdf",
            "title": "Illinois Attorney General",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/Mid "
            "American_summer2020.pdf",
            "title": "Mid-American",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/MISO_summer2020.pdf",
            "title": "MISO",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/NCLC_summer2020.pdf",
            "title": "NCLC",
        },
        {
            "href": "https://www.icc.illinois.gov/downloads/public/PJM_summer2020.pdf",
            "title": "PJM",
        },
    ]


def test_classification():
    assert parsed_item["classification"] == COMMISSION


def test_all_day():
    assert parsed_item["all_day"] is False
