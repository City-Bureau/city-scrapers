from datetime import datetime
from os.path import dirname, join

import pytest
import scrapy
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_police_district_councils import (
    ChiPoliceDistrictCouncilsSpider,
)

html_response = file_response(
    join(dirname(__file__), "files", "chi_police_district_councils.html"),
    url="https://ccpsa.chicago.gov/public-meeting-calendar/",
)

example_detail_page_response = file_response(
    join(
        dirname(__file__),
        "files",
        "chi_police_district_councils_example_detail_page.html",
    ),
    url="https://ccpsa.chicago.gov/public-meeting-calendar/event/3rd-district-council-september-12-2026/",  # noqa
)

json_response = file_response(
    join(dirname(__file__), "files", "chi_police_district_councils_listings.json"),
    url="https://ccpsa.chicago.gov/wp-admin/admin-ajax.php",
)

FORMDATA = {
    "action": "ccpsa_load_events",
    "nonce": "test",
    "tab": "all",
    "month": "8",
    "year": "2026",
    "per_page": "50",
    "sort": "desc",
    "context": "all-councils",
    "organizer_id": "0",
}


@pytest.fixture
def parsed_items():
    spider = ChiPoliceDistrictCouncilsSpider()
    with freeze_time("2026-09-04"):
        results = list(spider.parse(json_response, formdata=FORMDATA))
        meetings = [r for r in results if isinstance(r, Meeting)]
        detail_req = next(
            r
            for r in results
            if isinstance(r, scrapy.Request)
            and r.callback == spider._parse_meeting_details
        )
        meetings.extend(
            detail_req.callback(example_detail_page_response, **detail_req.cb_kwargs)
        )
        return meetings


def test_count(parsed_items):
    assert len(parsed_items) == 19


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "9th District Council"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 9, 30, 18, 30)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"]
        == "chi_police_district_councils/202609301830/x/9th_district_council"
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == TENTATIVE


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "Davis Square Park",
        "address": "4430 S Marshfield Ave Chicago, 60609",
    }


def test_source(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "https://ccpsa.chicago.gov/public-meeting-calendar/event/9th-district-council-september-30-2026/"  # noqa
    )


def test_links(parsed_items):
    assert parsed_items[0]["links"] == []
    assert parsed_items[18]["links"] == [
        {
            "href": "https://ccpsa.chicago.gov/wp-content/uploads/2025/12/Notice-and-Agenda-003-2026-9-5.pdf",  # noqa
            "title": "Notice-and-Agenda-003-2026-9-5.pdf",
        },
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == COMMISSION
