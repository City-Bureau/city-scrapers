from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, FORUM, NOT_CLASSIFIED
from city_scrapers_core.constants import CANCELLED, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_pollution_control import IlPollutionControlSpider

# TODO - Don't forget to implement this.
# test_minutes_response = file_response(
#     join(dirname(__file__), "files", "il_pollution_control.html"),
#     url="https://pcb.illinois.gov/ClerksOffice/MeetingMinutes",
# )

test_response = file_response(
    join(dirname(__file__), "files", "il_pollution_control.json"),
    url="https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents",
)
spider = IlPollutionControlSpider()

freezer = freeze_time("2019-10-03")
freezer.start()

parsed_items = [item for item in spider._parse_json(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 87


def test_title():
    # Define expected number of occurrences of each title:
    expected_title_counts = {"Board Meeting": 30,
                             "Brown Bag Seminar": 4,
                             "Hearing PCB 2012-035": 1,
                             "Hearing PCB 2014-003": 4,
                             "Hearing PCB 2018-083": 1,
                             "Hearing R2018-020": 9,
                             "Hearing R2018-024": 4,
                             "Hearing R2018-029": 2,
                             "Hearing R2018-030": 4,
                             "Hearing R2018-032": 12,
                             "Hearing R2019-001": 10,
                             "Hearing R2019-006": 2,
                             "Hearing R2019-018": 4}

    # Calculate actual counts from scraped items:
    all_titles = [item["title"] for item in parsed_items]
    unique_titles = set(all_titles)
    title_counts = {ut: len([t for t in all_titles if t == ut]) for ut in unique_titles}
    for title in title_counts:
        assert(title_counts[title] == expected_title_counts[title])


# def test_start():
#     assert parsed_items[0]["start"] == datetime(2019, 1, 1, 0, 0)


# def test_end():
#     assert parsed_items[0]["end"] == datetime(2019, 1, 1, 0, 0)


# def test_id():
#     assert parsed_items[0]["id"] == "EXPECTED ID"


def test_status():
    expected_counts = {CANCELLED: 11,
                       PASSED: 66,
                       TENTATIVE: 10}
    actual_counts = {}
    for key in expected_counts:
        actual_counts[key] = len([item for item in parsed_items if item['status'] == key])
        print(f"{key}: {actual_counts[key]}")
        assert actual_counts[key] == expected_counts[key]


# def test_location():
#     assert parsed_items[0]["location"] == {
#         "name": "EXPECTED NAME",
#         "address": "EXPECTED ADDRESS"
#     }


def test_source():
    expected_counts = {"https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=15564": 2,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=15596": 10,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=15588": 12,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=15480": 9,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=15559": 4,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=15565": 4,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=15607": 2,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=16703": 4,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=15594": 1,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=14216": 1,
                       "https://pcb.illinois.gov/Cases/GetCaseDetailsById?caseId=14657": 4,
                       "https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents": 34
                       }
    actual_counts = {}
    for key in expected_counts:
        actual_counts[key] = len([item for item in parsed_items if item['source'] == key])
        assert actual_counts[key] == expected_counts[key]


# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]


def test_classification():
    expected_counts = {BOARD: 30, FORUM: 4, NOT_CLASSIFIED: 53}
    actual_counts = {}
    for key in expected_counts:
        actual_counts[key] = len([item for item in parsed_items if item['classification'] == key])
        assert actual_counts[key] == expected_counts[key]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
