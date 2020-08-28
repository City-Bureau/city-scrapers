from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED, CANCELLED, PASSED
from city_scrapers_core.constants import TENTATIVE, COMMITTEE, COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ohare_noise import ChiOhareNoiseSpider

spider = ChiOhareNoiseSpider()

freezer = freeze_time("2020-08-22")
freezer.start()

test_response = file_response(
    join(dirname(__file__), "files/chi_ohare_noise", "chi_ohare_noise.html"),
    url="https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/2019/02/03/-",
)

parsed_items = [item for item in spider.ChiOhareNoiseSubSpider1().parse(test_response)]

freezer.stop()

def test_tests():
    assert len(parsed_items) == 45

parsed_sub_items = []
for i in range(5): 
    test_response_2 = file_response(
        join(dirname(__file__), "files/chi_ohare_noise", "chi_ohare_noise_meetings_sub_{0}.html".format(i+1)),
        url="https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/2019/02/03/-",
    )
    parsed_sub_items.append(spider.ChiOhareNoiseSubSpider1()._parse_details(test_response_2))

def test_title():
    assert parsed_sub_items[0]["title"] == "O'Hare Noise Compatibility Commission Meeting (via video/teleconference)"
    assert parsed_sub_items[1]["title"] == "Fly Quiet Committee (via video/teleconference)"
    assert parsed_sub_items[2]["title"] == "Executive Committee Meeting"
    assert parsed_sub_items[3]["title"] == "Executive Committee Meeting"
    assert parsed_sub_items[4]["title"] == "Fly Quiet Committee"


def test_description():
    assert parsed_sub_items[0]["description"] == "Join Zoom Meeting"
    assert parsed_sub_items[1]["description"] == "Join Zoom Meeting"
    assert parsed_sub_items[2]["description"] == ""
    assert parsed_sub_items[3]["description"] == ""
    assert parsed_sub_items[4]["description"] == ""


def test_start():
    assert parsed_sub_items[0]["start"] == datetime(2020, 6, 5, 8, 0)
    assert parsed_sub_items[1]["start"] == datetime(2020, 5, 26, 9, 30)
    assert parsed_sub_items[2]["start"] == datetime(2020, 2, 10, 10, 30)
    assert parsed_sub_items[3]["start"] == datetime(2020, 1, 6, 10, 30)
    assert parsed_sub_items[4]["start"] == datetime(2020, 12, 8, 9, 30)


def test_end():
    assert parsed_sub_items[0]["end"] == datetime(2020, 6, 5, 9, 0)
    assert parsed_sub_items[1]["end"] == datetime(2020, 5, 26, 10, 30)
    assert parsed_sub_items[2]["end"] == datetime(2020, 2, 10, 11, 30)
    assert parsed_sub_items[3]["end"] == datetime(2020, 1, 6, 11, 30)
    assert parsed_sub_items[4]["end"] == datetime(2020, 12, 8, 10, 30)


def test_status():
    assert parsed_sub_items[0]["status"] == "passed"
    assert parsed_sub_items[1]["status"] == "passed"
    assert parsed_sub_items[2]["status"] == "passed"
    assert parsed_sub_items[3]["status"] == "passed"
    assert parsed_sub_items[4]["status"] == "tentative"


def test_location():
    assert parsed_sub_items[0]["location"] == {
        "name": "(via video/teleconference)",
        "address": "(via video/teleconference)"
    }
    assert parsed_sub_items[1]["location"] == {
        "name": "(via video/teleconference)",
        "address": "(via video/teleconference)"
    }
    assert parsed_sub_items[2]["location"] == {
        "name": "Aviation Administration Building",
        "address": "10510 W. Zemke Rd"
    }
    assert parsed_sub_items[3]["location"] == {
        "name": "Aviation Administration Building",
        "address": "10510 W. Zemke Rd"
    }
    assert parsed_sub_items[4]["location"] == {
        "name": "Chicago Dept. of Aviation Building",
        "address": "10510 W. Zemke Road, Chicago, IL, Conference Room 1"
    }


def test_source():
    assert parsed_sub_items[0]["source"] == "https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/2019/02/03/-"
    assert parsed_sub_items[1]["source"] == "https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/2019/02/03/-"
    assert parsed_sub_items[2]["source"] == "https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/2019/02/03/-"
    assert parsed_sub_items[3]["source"] == "https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/2019/02/03/-"
    assert parsed_sub_items[4]["source"] == "https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/2019/02/03/-"


# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]


def test_classification():
    assert parsed_sub_items[0]["classification"] == COMMISSION
    assert parsed_sub_items[1]["classification"] == COMMITTEE
    assert parsed_sub_items[2]["classification"] == COMMITTEE
    assert parsed_sub_items[3]["classification"] == COMMITTEE
    assert parsed_sub_items[4]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_sub_items)
def test_all_day(item):
    assert item["all_day"] is False
