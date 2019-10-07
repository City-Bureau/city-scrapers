from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMITTEE, BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_employment_solutions_corp import DetEmploymentSolutionsCorpSpider

test_pdf_response = file_response(
    join(dirname(__file__), "files", "det_employment_solutions_corp.pdf"),
    url=(
        "https://www.descmiworks.com/wp-content/uploads/2019-DESC-Board-And-Committee-Calendar-Amended-08-22-2019.pdf"  # noqa
    ),
    mode="rb",
)
test_response = file_response(
    join(dirname(__file__), "files", "det_employment_solutions_corp.html"),
    url="https://www.descmiworks.com/about-us/public-meetings/",
)
spider = DetEmploymentSolutionsCorpSpider()

freezer = freeze_time("2019-07-20")
freezer.start()

spider._parse_schedule_pdf(test_pdf_response)
parsed_items = sorted(
    [item for item in spider._parse_documents(test_response)],
    key=itemgetter("start"),
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 25


def test_title():
    assert parsed_items[0]["title"] == "Audit and Finance Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 31, 10, 00)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 1, 31, 11, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0][
        "id"] == "det_employment_solutions_corp/201901311000/x/audit_and_finance_committee"  # noqa


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "https://www.descmiworks.com/about-us/public-meetings/"


def test_links():
    assert parsed_items[0]["links"] == [{
        "href":
            "https://www.descmiworks.com/wp-content/uploads/Audit-and-Finance-Committe-Meeting-January-31-2019.pdf",  # noqa
        "title": "Minutes"
    }]
    assert parsed_items[-1]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[4]["classification"] == BOARD


def test_all_day():
    assert parsed_items[0]["all_day"] is False
