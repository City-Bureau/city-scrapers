from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_pubhealth import ChiPubHealthSpider

test_response_year_pages = file_response(
    join(dirname(__file__), "files", "chi_pubhealth.html"),
    url="https://www.chicago.gov/city/en/depts/cdph/supp_info.html",
)
test_response_2024_page = file_response(
    join(dirname(__file__), "files", "chi_pubhealth_2024.html"),
    url="https://www.chicago.gov/city/en/depts/cdph/supp_info/boh/2024-board-of-health-meetings.html",  # noqa
)

spider = ChiPubHealthSpider()

freezer = freeze_time("2024-07-24")
freezer.start()

parsed_year_pages = [item for item in spider.parse(test_response_year_pages)]
parsed_meetings = [
    item for item in spider._parse_year_page(test_response_2024_page)
]  # noqa
parsed_meeting = parsed_meetings[0]
freezer.stop()


def test_page_tally():
    assert len(parsed_year_pages) == 2


def test_meetings_tally():
    assert len(parsed_meetings) == 6


def test_meeting_all_day():
    assert parsed_meeting["all_day"] is False


def test_meeting_classification():
    assert parsed_meeting["classification"] == "Board"


def test_meeting_description():
    assert parsed_meeting["description"] == ""


def test_meeting_end():
    assert parsed_meeting["end"] == datetime(2024, 1, 31, 10, 30)


def test_meeting_id():
    assert (
        parsed_meeting["id"]
        == "chi_pubhealth/202401310900/x/board_of_health_meeting"  # noqa
    )


def test_meeting_links():
    expected_links = [
        {
            "title": "Agenda",
            "href": "https://www.chicago.gov/content/dam/city/depts/cdph/policy_planning/Board_of_Health/2024/2024-01-Jan-BOH-Agenda.pdf",  # noqa
        },
        {
            "title": "Minutes",
            "href": "https://www.chicago.gov/content/dam/city/depts/cdph/policy_planning/Board_of_Health/2024/BOH-Jan-2024-Minutes.pdf",  # noqa
        },
        {
            "title": "Presentation: Dr. Olusimbo Ige - CDPH 2023 Accomplishments and 2024 Priorities",  # noqa
            "href": "https://www.chicago.gov/content/dam/city/depts/cdph/policy_planning/Board_of_Health/2024/CDPH-2023-Accomplishments_Jan-2024.pdf",  # noqa
        },
    ]
    assert parsed_meeting["links"] == expected_links


def test_meeting_location():
    expected_location = {
        "name": "DePaul Center",
        "address": "333 S State St, 2nd Floor, Room 200",
    }
    assert parsed_meeting["location"] == expected_location


def test_meeting_source():
    assert (
        parsed_meeting["source"]
        == "https://www.chicago.gov/city/en/depts/cdph/supp_info/boh/2024-board-of-health-meetings.html"  # noqa
    )


def test_meeting_start():
    assert parsed_meeting["start"] == datetime(2024, 1, 31, 9, 0)


def test_meeting_status():
    assert parsed_meeting["status"] == "passed"


def test_meeting_time_notes():
    assert parsed_meeting["time_notes"] == ""


def test_meeting_title():
    assert parsed_meeting["title"] == "Board of Health meeting"
