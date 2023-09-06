from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_northwest_home_equity import ChiNorthwestHomeEquitySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_northwest_home_equity.html"),
    url="https://nwheap.com/category/meet-minutes-and-agendas/",
)

url_to_local = {"https://nwheap.com/category/meet-minutes-and-agendas/": "chi_northwest_home_equity.html",
                "https://nwheap.com/events/governing-commissioners-public-meeting-18/": "1.html",
                "https://nwheap.com/events/governing-commissioners-public-meeting-17/": "2.html",
                "https://nwheap.com/events/governing-commissioners-public-meeting-16/": "3.html",
                "https://nwheap.com/events/governing-commissioners-public-meeting-15/": "4.html",
                "https://nwheap.com/events/governing-commissioners-public-meeting-14/": "5.html",
                "https://nwheap.com/events/governing-commissioners-public-meeting-13/": "6.html",
                "https://nwheap.com/events/governing-commissioners-public-meeting-12/": "7.html",}

for link, local in url_to_local.items():
    url_to_local[link] = join(dirname(__file__), "files", local)

spider = ChiNorthwestHomeEquitySpider()

freezer = freeze_time("2023-09-04")
freezer.start()



freezer.stop()


# def test_tests():
#     print("Please write some tests for this spider or at least disable this one.")
#     assert False


"""
Uncomment below
"""

def test_title():
    assert parsed_items[0]["title"] == "Governing Commissioners Public Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""

#{"title": "Governing Commissioners Public Meeting", "description": "", "classification": "Commission", "start": "2022-12-15 18:30:00", "end": "2022-12-15 19:30:00", "all_day": false, "time_notes": "", "location": {"address": "Northwest Home Equity Assurance Program", "name": ""}, "links": [{"href": "", "title": ""}], "source": "https://nwheap.com/events/governing-commissioners-public-meeting-12/", "id": "chi_northwest_home_equity/202212151830/x/governing_commissioners_public_meeting", "status": "passed"},

def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 15, 18, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 12, 15, 19, 30)


# def test_time_notes():
#     assert parsed_items[0]["time_notes"] == "EXPECTED TIME NOTES"


# def test_id():
#     assert parsed_items[0]["id"] == "EXPECTED ID"


# def test_status():
#     assert parsed_items[0]["status"] == "EXPECTED STATUS"


# def test_location():
#     assert parsed_items[0]["location"] == {
#         "name": "EXPECTED NAME",
#         "address": "EXPECTED ADDRESS"
#     }


# def test_source():
#     assert parsed_items[0]["source"] == "EXPECTED URL"


# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]


# def test_classification():
#     assert parsed_items[0]["classification"] == NOT_CLASSIFIED


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
