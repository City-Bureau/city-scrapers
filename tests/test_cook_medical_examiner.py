from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE
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
    agenda = [
        'Roll Call',
        'Review and approval of General Meeting Minutes from July 20 and October 19, 2018',
        'Public Comment', 'Reports from:\n',
        "Medical Examiner's Office: Deputy Chief Medical Examiner, Eimad Zakariya, MD\n",
        'General Report', '\n', '\n', 'Vice-Chairman, Jason Moran\n',
        'Committee Attendance & Annual Report', '\n', '\n', 'Old Business', 'New Business',
        'Adjournment - Next Meeting: April 19, 2019'
    ]
    clean_agenda = "\n".join([a.strip().replace("\\", "") for a in agenda if a != ''])
    assert parsed_items[0]["description"] == clean_agenda


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 18, 11, 00)
    assert parsed_items[1]["start"] == datetime(2019, 4, 19, 11, 00)
    assert parsed_items[4]["start"] == datetime(2020, 1, 17, 11, 00)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 1, 18, 12, 30)
    assert parsed_items[1]["end"] == datetime(2019, 4, 19, 12, 30)


def test_status():
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[1]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Cook County Medical Examiner’s Office",
        "address": "2121 W Harrison; Chicago, IL 60612",
        'coordinates': {
            'latitude': None,
            'longitude': None
        }
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.cookcountyil.gov/service/" \
                                        "medical-examiners-advisory-committee"


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
