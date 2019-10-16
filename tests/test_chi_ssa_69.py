# from datetime import datetime
from os.path import dirname, join

# import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_69 import ChiSsa69Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_69.html"),
    url="https://auburngresham.wixsite.com/ssa69/calendar",
)
spider = ChiSsa69Spider()

freezer = freeze_time("2019-10-09")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()
"""
Uncomment below
"""

# def test_title():
#     assert parsed_items[0]["title"] == "EXPECTED TITLE"

# def test_title():
#        expected_value = "GAGDC & SSA#69 Neighborhood Opportunity Fund Grant Training"
#    assert parsed_items[1]["title"] == expected_value

# def test_description():
#     assert parsed_items[0]["description"] == "EXPECTED DESCRIPTION"

# def test_start():
#     assert parsed_items[0]["start"] == datetime(2019, 1, 1, 0, 0)

# def test_end():
#     assert parsed_items[0]["end"] == datetime(2019, 1, 1, 0, 0)

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


def test_classification():
    print("len=" + str(len(parsed_items)))
    # print(parsed_items[2]['title'])
    print(parsed_items[0])
    print("\n\n")
    print(parsed_items[1])
    print("\n\n")
    print(parsed_items[2])
    print("\n\n")
    print(parsed_items[3])
    print("\n\n")
    print(parsed_items[4])
    print("\n\n")
    print(parsed_items[5])
    print("\n\n")
    print(parsed_items[6])
    print("\n\n")
    print(parsed_items[7])
    print("\n\n")
    print(parsed_items[8])
    print("\n\n")
    print(parsed_items[9])
    print("\n\n")

    print("len=" + str(len(parsed_items)))
    # exit()

    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
