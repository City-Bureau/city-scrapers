from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_4 import ChiSsa4Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_4.html"),
    url="https://95thstreetba.org/events/95th-street-business-association-meeting-4/",
)
spider = ChiSsa4Spider()

freezer = freeze_time("2020-06-25")
freezer.start()

item = spider._parse_event(test_response)

freezer.stop()


def test_title():
    assert item["title"] == "95th Street Business Association"


def test_description():
    desc = ""
    assert item["description"].replace("\xa0", " ") == desc


def test_start():
    assert item["start"] == datetime(2018, 9, 25, 8, 0)


def test_end():
    assert item["end"] == datetime(2018, 9, 25, 9, 0)


def test_time_notes():
    assert item["time_notes"] == ""


def test_id():
    id = "chi_ssa_4/201809250800/x/95th_street_business_association"
    assert item["id"] == id


def test_status():
    assert item["status"] == PASSED


def test_location():
    assert item["location"] == {
        "name": " Original Pancake House",
        "address": "10437 S. Western Ave. Chicago, IL 60643 United States",
    }


def test_source():
    src = "https://95thstreetba.org/events/95th-street-business-association-meeting-4/"
    assert item["source"] == src


def test_links():
    assert item["links"] == [
        {
            "href": "https://95thstreetba.org/wp-content/uploads/SEP18minutes.pdf",
            "title": "Minutes",
        }
    ]


def test_classification():
    assert item["classification"] == COMMISSION


def test_all_day():
    assert item["all_day"] is False
