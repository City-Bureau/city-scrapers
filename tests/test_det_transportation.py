from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import FORUM, PASSED
from city_scrapers_core.utils import file_response
# import pytest
from freezegun import freeze_time

from city_scrapers.spiders.det_transportation import DetTransportationSpider

test_response = file_response(
    join(dirname(__file__), "files", "det_transportation.html"),
    url='https://detroitmi.gov/events/community-input-meeting-0'
)
spider = DetTransportationSpider()

freezer = freeze_time("2019-04-21")
freezer.start()

item = spider.parse_event_page(test_response)

freezer.stop()


def test_title():
    assert item["title"] == "Community Input Meeting"


def test_description():
    # fix difficult spacing in the description
    cleaned = item['description']
    ours = ' '.join(cleaned.split())

    good_description = """Please join us for the first community input meeting of the year!
                    January 17, 2019 5:00pm - 7:00pm
                    at the DDOT Admin Bldg. Topics Include:
                    • Review of December 2018 concerns
                    • New Fare Overview (Implementing May 1, 2019)"""

    theirs = ' '.join(good_description.split())

    assert (ours == theirs)


def test_start():
    assert item["start"] == datetime(2019, 1, 17, 17, 0)


def test_end():
    assert item["end"] == datetime(2019, 1, 17, 19, 0)


def test_time_notes():
    assert item["time_notes"] == ''


def test_id():
    assert item["id"] == 'det_transportation/201901171700/x/community_input_meeting'


def test_status():
    assert item["status"] == PASSED


def test_location():
    correct_location = {
        'address': '1301 East Warren Avenue, Detroit MI 48207',
        'name': 'Detroit Department of Transportation'
    }

    # this test is unusually sensitive to whitespace
    for key in item["location"]:
        ours = item["location"][key].lstrip()
        theirs = correct_location[key].lstrip()
        assert (ours == theirs)


def test_source():
    assert item["source"] == 'https://detroitmi.gov/events/community-input-meeting-0'


def test_links():
    assert item["links"] == []


def test_classification():
    assert item["classification"] == FORUM


def test_all_day():
    assert item["all_day"] is False
