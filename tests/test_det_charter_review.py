from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_charter_review import DetCharterReviewSpider

test_response = file_response(
    join(dirname(__file__), "files", "det_charter_review.html"),
    url=(
        "https://detroitmi.gov/events/detroit-charter-revision-commission-meeting-economic-growth-development-3-20-19"  # noqa
    ),
)
spider = DetCharterReviewSpider()

freezer = freeze_time("2019-04-23")
freezer.start()

item = spider.parse_event_page(test_response)

freezer.stop()


def test_title():
    assert item["title"] == "Charter Review Commission"


def test_description():
    assert item["description"] == (
        'The Detroit Charter Revision Committee - Economic Growth & '
        'Development Sub-Committee is holding a meeting. The Public is '
        'invited and encouraged to attend. Additional information '
        'regarding this meeting may be obtained from the Office of the '
        'City Clerk at (313) 224-3266.'
    )


def test_start():
    assert item["start"] == datetime(2019, 3, 20, 12, 0)


def test_end():
    assert item["end"] == datetime(2019, 3, 20, 15, 0)


def test_time_notes():
    assert item["time_notes"] == "Estimated 3 hour duration"


def test_id():
    assert item["id"] == "det_charter_review/201903201200/x/charter_review_commission"


def test_status():
    assert item["status"] == PASSED


def test_location():
    assert item["location"] == {
        "name": "Detroit Association of Black Organizations",
        "address": "12048 Grand River Ave., Detroit, MI 48204",
    }


def test_source():
    assert item[
        "source"
    ] == "https://detroitmi.gov/events/detroit-charter-revision-commission-meeting-economic-growth-development-3-20-19"  # noqa


def test_links():
    assert item["links"] == [{
        'href':
            'https://detroitmi.gov/sites/detroitmi.localhost/files/events/2019-03/cal%203-20-19%20Charter%20Revision%20Commission_Economic%20and%20Development%20Sub-Committee.pdf',  # noqa
        'title':
            'cal 3-20-19 Charter Revision Commission_Economic and Development Sub-Committee.pdf'
    }]


def test_classification():
    assert item["classification"] == COMMITTEE


def test_all_day():
    assert item["all_day"] is False
