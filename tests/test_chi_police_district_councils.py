from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_police_district_councils import (
    ChiPoliceDistrictCouncilsSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "chi_police_district_councils", "DC001.html"),
    url="https://www.chicago.gov/city/en/depts/ccpsa/supp_info/district-council-pages/DC001.html",  # noqa
)

meeting_response = file_response(
    join(
        dirname(__file__),
        "files",
        "chi_police_district_councils",
        "Notice-and-Agenda-001-2023-06-06.pdf",
    ),
    url="https://www.chicago.gov/content/dam/city/depts/ccpsa/district-council-agendas/dc-001/notices-and-agendas/Notice-and-Agenda-001-2023-06-06.pdf",  # noqa
    mode="rb",
)

meeting_response_closed = file_response(
    join(
        dirname(__file__),
        "files",
        "chi_police_district_councils",
        "Notice-and-Agenda-001-2023.06.01-closed.pdf",
    ),
    url="https://www.chicago.gov/content/dam/city/depts/ccpsa/district-council-agendas/dc-001/notices-and-agendas/Notice-and-Agenda-001-2023.06.01-closed.pdf",  # noqa
    mode="rb",
)


spider = ChiPoliceDistrictCouncilsSpider()

freezer = freeze_time("2023-06-16")
freezer.start()

requests = [item for item in spider.parse(test_response)]
parsed_items = []
for request in requests:
    if request.url == meeting_response.url:
        meeting_response.request = request
        parsed_items += [item for item in spider._parse_meeting(meeting_response)]
    elif request.url == meeting_response_closed.url:
        meeting_response_closed.request = request
        parsed_items += [
            item for item in spider._parse_meeting(meeting_response_closed)
        ]

freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Chicago Police District Council 001 Regular Meeting"
    )
    assert parsed_items[1]["title"] == "Chicago Police District Council 001 Meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2023, 6, 6, 17, 30)
    assert parsed_items[1]["start"] == datetime(2023, 6, 1, 0, 0)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_police_district_councils/202306061730/x/chicago_police_district_council_001_regular_meeting"  # noqa
    )
    assert (
        parsed_items[1]["id"]
        == "chi_police_district_councils/202306010000/x/chicago_police_district_council_001_meeting"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[1]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Maggie Daley Fieldhouse, ",
        "address": "",
    }
    assert parsed_items[1]["location"] == {}


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.chicago.gov/city/en/depts/ccpsa/supp_info/district-council-pages/DC001.html"  # noqa
    )
    assert (
        parsed_items[1]["source"]
        == "https://www.chicago.gov/city/en/depts/ccpsa/supp_info/district-council-pages/DC001.html"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/ccpsa/district-council-agendas/dc-001/notices-and-agendas/Notice-and-Agenda-001-2023-06-06.pdf",  # noqa
            "title": "agenda",
        }
    ]
    assert parsed_items[1]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/ccpsa/district-council-agendas/dc-001/notices-and-agendas/Notice-and-Agenda-001-2023.06.01-closed.pdf",  # noqa
            "title": "agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
