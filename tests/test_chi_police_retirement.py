from datetime import datetime
from os.path import dirname, join

import pytest
from freezegun import freeze_time
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response

from city_scrapers.spiders.chi_police_retirement import ChiPoliceRetirementSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_police_retirement.html"),
    url="http://www.chipabf.org/ChicagoPolicePension/MonthlyMeetings.html",
)
spider = ChiPoliceRetirementSpider()

freezer = freeze_time("2019-05-05")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


"""
Uncomment below
"""

def test_title():
    assert parsed_items[0]["title"] == "Board Meetings of The Policemen's Annuity & Benefit Fund"


def test_description():
    assert parsed_items[0]["description"] == 'Listed below are the dates scheduled for the regular Board meetings of The Policemen’s Annuity & Benefit Fund. All meetings are scheduled to begin at 9:00 A.M., and are to be held in the office of the Fund.'


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 31, 9, 0)


def test_end():
    assert parsed_items[0]["end"] == None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == None


def test_id():
    assert parsed_items[0]["id"] == 'chi_police_retirement/201901310900/x/board_meetings_of_the_policemen_s_annuity_benefit_fund'


def test_status():
    assert parsed_items[0]["status"] == 'passed'


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Policemen's Annuity and Benefit Fund",
        "address": '221 North LaSalle Street, Suite 1626, Chicago, '
                         'Illinois 60601-1203'
    }


def test_source():
    assert parsed_items[0]["source"] == 'http://www.chipabf.org/ChicagoPolicePension/MonthlyMeetings.html'


def test_links():

    assert parsed_items[0]["links"] == [{'href': 'https://www.chipabf.org/ChicagoPolicePension/PDF/Agenda/2019/2019AGENDA01.pdf',
        'title': 'Agenda'},
     {'href': 'www.chipabf.org/ChicagoPolicePension/PDF/Minutes/2019/2019MINUTES01.pdf',
       	'title': 'Minutes'}]


def test_classification():
    assert parsed_items[0]["classification"] == 'Board'


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
