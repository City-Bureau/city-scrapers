from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, FORUM, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_il_medical_district import ChiIlMedicalDistrictSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_il_medical_district.html"),
    url="http://medicaldistrict.org/commission/",
)
spider = ChiIlMedicalDistrictSpider()

freezer = freeze_time("2019-04-11")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 35


def test_title():
    assert parsed_items[0]["title"] == "Illinois Medical District Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 5, 21, 8, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0][
        "id"] == "chi_il_medical_district/201905210800/x/illinois_medical_district_commission"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "http://medicaldistrict.org/commission/"


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[4]["links"] == [
        {
            'title': 'Commission Meeting Agenda',
            'href': 'http://medicaldistrict.org/wp-content/uploads/2019/03/agenda_031919.pdf'
        },
        {
            'title': 'Commission Meeting Notice',
            'href':
                'http://medicaldistrict.org/wp-content/uploads/2019/03/notice_of_commission_meeting.pdf'  # noqa
        }
    ]
    assert parsed_items[19]["links"] == [{
        'title': 'Use-Value Hearing',
        'href':
            'http://medicaldistrict.org/wp-content/uploads/pdf/Notice_of_Use_Value_Hearing_-_8_Hospitality_Group.pdf'  # noqa
    }]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
    assert parsed_items[13]["classification"] == FORUM


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
