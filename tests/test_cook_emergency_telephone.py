from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import FORUM, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_emergency_telephone import CookEmergencyTelephoneSpider

test_pdf_response = file_response(
    join(dirname(__file__), "files", "cook_emergency_telephone_schedule.pdf"),
    url=(
        "https://cookcounty911.com/wp-content/uploads/pdfs/schedule.pdf"  # noqa
    ),
    mode="rb",
)

test_response = file_response(
    join(dirname(__file__), "files", "cook_emergency_telephone.html"),
    url="https://cookcounty911.com",
)
spider = CookEmergencyTelephoneSpider()

freezer = freeze_time("2020-05-27")
freezer.start()

# parse in this case is a generator, it won't get executed unless iterated over
for _ in spider.parse(test_response):
    pass

spider._parse_schedule_pdf(test_pdf_response)

parsed_items = sorted(
    [item for item in spider._parse_documents(test_response)],
    key=itemgetter("start"),
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 11


def test_title():
    assert parsed_items[0]["title"] == "Cook County Emergency Telephone System Board Public Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 2, 28, 10, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2020, 2, 28, 12, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == (
        "cook_emergency_telephone/202002281030/x/"
        "cook_county_emergency_telephone_system_board_public_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Conference Room",
        "address": "1401 S. Maybrook Drive, Maywood, IL 60153"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.cookcounty911.com/"


def test_links():
    assert parsed_items[0]["links"] == [{
        'title': 'Minutes',
        'href': 'https://cookcounty911.com/minutes'
    }, {
        'title': 'Agenda',
        'href': 'https://cookcounty911.com/agenda'
    }]


def test_classification():
    assert parsed_items[0]["classification"] == FORUM


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
