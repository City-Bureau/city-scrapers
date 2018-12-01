from datetime import date, time

from tests.utils import file_response

from city_scrapers.constants import BOARD, PASSED
from city_scrapers.spiders.chi_city_college import ChiCityCollegeSpider

test_response = file_response('files/chi_city_college.html')
spider = ChiCityCollegeSpider()
item = spider.parse_event_page(test_response)


def test_name():
    assert item['name'] == 'Board of Trustees: November 2018 Regular Board Meeting'


def test_start_time():
    assert item['start']['time'] == time(9, 0)
    assert item['start']['date'] == date(2018, 11, 1)
    assert item['start']['note'] is None


def test_end_time():
    assert item['end']['time'] == time(12, 0)
    assert item['end']['date'] == date(2018, 11, 1)
    assert item['end']['note'] is None


def test_id():
    assert item[
        'id'
    ] == 'chi_city_college/201811010900/x/board_of_trustees_november_2018_regular_board_meeting'


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == BOARD


def test_status():
    assert item['status'] == PASSED


def test_location():
    assert item['location'] == {
        'name': 'Harold Washington College',
        'address': '30 E. Lake Street, 11th Floor, Chicago, IL 60601',
        'neighborhood': None,
    }


def test_description():
    assert item[
        'event_description'
    ] == '\u200b The November regularly scheduled meeting of the Board of Trustees of Community College District No. 508, County of Cook and State of Illinois, has been scheduled for Thursday, November 1, 2018 at 9:00 a.m., Harold Washington College, 30 E. Lake Street, 11th Floor, Chicago, IL 60601.  Any individual planning to attend this meeting who will need an accommodation under the Americans with Disabilities Act should notify the Board Office, at (312) 553-2515 or at requesttospeak@ccc.edu.'  # noqa


def test__type():
    assert item['_type'] == 'event'
