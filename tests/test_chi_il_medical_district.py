from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, FORUM, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_il_medical_district import ChiIlMedicalDistrictSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_il_medical_district.html"),
    url="http://medicaldistrict.org/commission/",
)
spider = ChiIlMedicalDistrictSpider()

freezer = freeze_time("2019-05-20")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)], key=itemgetter("start")
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 35


def test_title():
    assert parsed_items[0]["title"] == "Illinois Medical District Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2016, 5, 17)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_il_medical_district/201605170000/x/illinois_medical_district_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[-4]["status"] == TENTATIVE
    assert parsed_items[-1]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == "http://medicaldistrict.org/commission/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://medicaldistrict.org/wp-content/uploads/pdf/CommissionMeetingMinutesMay172016.pdf",  # noqa
            "title": "Commission Meeting Minutes",
        },
        {
            "href": "http://medicaldistrict.org/wp-content/uploads/pdf/AgendaRevised-051716.pdf",  # noqa
            "title": "Meeting Agenda",
        },
    ]
    assert parsed_items[-4]["links"] == [
        {
            "href": "http://medicaldistrict.org/wp-content/uploads/2019/05/agenda_052119.pdf",  # noqa
            "title": "Commission Meeting Agenda",
        },
        {
            "href": "http://medicaldistrict.org/wp-content/uploads/2019/05/notice-of-commission-meeting_05212019.pdf",  # noqa
            "title": "Commission Meeting Notice",
        },
    ]
    assert parsed_items[-1]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
    assert parsed_items[1]["classification"] == FORUM


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
