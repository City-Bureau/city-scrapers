from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_justice_advisory import CookJusticeAdvisorySpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_justice_advisory.html"),
    url="https://www.cookcountyil.gov/event/jac-council-meeting-18",
)

test_detail_response = file_response(
    join(dirname(__file__), "files", "cook_justice_advisory_details.html"),
    url=("https://www.cookcountyil.gov/service/justice-advisory-council-meetings"),
)

spider = CookJusticeAdvisorySpider()
freezer = freeze_time("2020-6-12")
freezer.start()
spider._parse_links(test_detail_response)
item = spider._parse_event(test_response)
freezer.stop()


def test_title():
    assert item["title"] == "JAC Council Meeting"


def test_start():
    assert item["start"] == datetime(2020, 1, 9, 8, 30)


def test_end():
    assert item["end"] == datetime(2020, 1, 9, 10, 00)


def test_time_notes():
    assert item["time_notes"] == ""


def test_id():
    assert item["id"] == "cook_justice_advisory/202001090830/x/jac_council_meeting"


def test_all_day():
    assert item["all_day"] is False


def test_classification():
    assert item["classification"] == ADVISORY_COMMITTEE


def test_status():
    assert item["status"] == PASSED


def test_location():
    assert item["location"] == {
        "name": "",
        "address": "69 W. Washington 22nd Floor Conference Room D Chicago IL 60602",
    }


def test_sources():
    assert item["source"] == "https://www.cookcountyil.gov/event/jac-council-meeting-18"


def test_description():
    assert item["description"] == "JAC Council Meeting"


def test_links():
    assert item["links"] == [
        {
            "href": "https://www.cookcountyil.gov/sites/default/files/jac_council_agenda_1.9.2020_1.pdf",
            "title": "Agenda",
        }
    ]
