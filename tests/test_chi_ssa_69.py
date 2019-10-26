# from datetime import datetime
from os.path import dirname, join

# import pytest
from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_69 import ChiSsa69Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_69.json"),
    url="https://auburngresham.wixsite.com/ssa69/calendar",
)

spider = ChiSsa69Spider()

freezer = freeze_time("2019-10-09")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == 'SSA #69 Commissioners'
    assert parsed_items[1]["title"] == 'CPD 006th District C.A.P.S Business Subcommittee Meetings'
    assert parsed_items[2]["title"] == 'CPD 006th District C.A.P.S Business Subcommittee Meetings'


def test_description():
    assert parsed_items[0]["description"] == (
        ' SSA #69 Commissioners Meeting:\n'
        ' Corresponding Dates: \n'
        'February 12, 2019; July 23, 2019; and  November 12, 2019\n'
        ' Location: 7901 S. Racine, Chicago, IL 60620\n'
        ' Time: 8:30 am to 10:00 am'
    )
    assert parsed_items[1]["description"] == (
        'CPD 006th District C.A.P.S, Business Subcommittee Meetings\n'
        'Dates: 2nd Tuesday of each month\n'
        'Location: 006th District Police Station Community Room\n'
        '7808 S. Halsted , Chicago, IL 60620'
    )
    assert parsed_items[2]["description"] == (
        'CPD 006th District C.A.P.S, Business Subcommittee Meetings\n'
        'Dates: 2nd Tuesday of each month\n'
        'Location: 006th District Police Station Community Room\n'
        '7808 S. Halsted , Chicago, IL 60620'
    )


def test_start():
    assert str(parsed_items[0]["start"]) == "2019-11-12 09:30:00"
    assert str(parsed_items[1]["start"]) == "2019-10-08 18:00:00"
    # I think this recurring meeting has different start times
    # because of the upcoming Daylight Savings Time change
    # I wonder if this test will fail after Daylight Savings hits
    assert str(parsed_items[2]["start"]) == "2019-11-12 19:00:00"


def test_end():
    assert str(parsed_items[0]["end"]) == "2019-11-12 11:00:00"
    assert str(parsed_items[1]["end"]) == "2019-10-08 19:00:00"
    # I think this recurring meeting has different end times
    # because of the upcoming Daylight Savings Time change
    # I wonder if this test will fail after Daylight Savings hits
    assert str(parsed_items[2]["end"]) == "2019-11-12 20:00:00"


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ''
    assert parsed_items[1]["time_notes"] == ''
    assert parsed_items[2]["time_notes"] == ''


def test_id():
    assert parsed_items[0]["id"] == 'chi_ssa_69/201911120930/x/ssa_69_commissioners'
    assert parsed_items[1][
        "id"
    ] == 'chi_ssa_69/201910081800/x/cpd_006th_district_c_a_p_s_business_subcommittee_meetings'
    assert parsed_items[2][
        "id"
    ] == 'chi_ssa_69/201911121900/x/cpd_006th_district_c_a_p_s_business_subcommittee_meetings'


def test_status():
    assert parsed_items[0]["status"] == 'tentative'
    assert parsed_items[1]["status"] == 'passed'
    assert parsed_items[2]["status"] == 'tentative'


def test_location():
    assert parsed_items[0]["location"] == {
        "name": '',
        "address": '7901 S Racine Ave, Chicago, IL 60620, USA'
    }
    assert parsed_items[1]["location"] == {
        "name": '006th district police station',
        "address": '7808 S. Halsted , Chicago, IL 60620'
    }
    assert parsed_items[2]["location"] == {
        "name": '006th district police station',
        "address": '7808 S. Halsted , Chicago, IL 60620'
    }


def test_source():
    url_p = 'https://www.google.com/calendar/event?eid='
    url_s1 = 'MWQxMDU2cDhmZmVjZjBmN2JqZHRuMmtncDEgZ2FnZGNjaGljYWdvQG0&ctz=GMT-05:00'
    url_s2 = 'MmM4N3B2dWpwb2RlNTJzMW1iM21lNmx1dDMgZ2FnZGNjaGljYWdvQG0&ctz=GMT-05:00'
    url_s3 = 'Nm5odWltcTZnN290dXVrdmVrZ3Y5aG9rNjEgZ2FnZGNjaGljYWdvQG0&ctz=GMT-05:00'
    assert parsed_items[0]["source"] == url_p + url_s1
    assert parsed_items[1]["source"] == url_p + url_s2
    assert parsed_items[2]["source"] == url_p + url_s3


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[1]["links"] == []
    assert parsed_items[2]["links"] == []


def test_classification():
    print("len=" + str(len(parsed_items)))

    print(parsed_items[0])
    print("\n\n")
    print(parsed_items[1])
    print("\n\n")
    print(parsed_items[2])
    print("\n\n")

    print("len=" + str(len(parsed_items)))
    # exit()

    assert parsed_items[0]["classification"] == COMMISSION
    assert parsed_items[1]["classification"] == COMMITTEE
    assert parsed_items[2]["classification"] == COMMITTEE


def test_all_day():
    assert parsed_items[0]["all_day"] is False
    assert parsed_items[1]["all_day"] is False
    assert parsed_items[2]["all_day"] is False
