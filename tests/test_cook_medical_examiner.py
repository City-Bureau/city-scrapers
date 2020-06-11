from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_medical_examiner import CookMedicalExaminerSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_medical_examiner.html"),
    url="https://www.cookcountyil.gov/service/medical-examiners-advisory-committee",
)
spider = CookMedicalExaminerSpider()

freezer = freeze_time("2019-03-14")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Medical Examiner's Advisory Committee"


def test_number():
    assert len(parsed_items) == 5


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 18, 11, 00)
    assert parsed_items[1]["start"] == datetime(2019, 4, 19, 11, 00)
    assert parsed_items[4]["start"] == datetime(2020, 1, 17, 11, 00)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 1, 18, 12, 30)
    assert parsed_items[1]["end"] == datetime(2019, 4, 19, 12, 30)


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[1]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.cookcountyil.gov/service/medical-examiners-advisory-committee"
    )  # noqa


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
