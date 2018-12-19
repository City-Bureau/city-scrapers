from datetime import date, time

from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import BOARD, PASSED
from city_scrapers.spiders.chi_city_college import ChiCityCollegeSpider

freezer = freeze_time('2018-12-19')
freezer.start()
test_response = file_response(
    'files/chi_city_college.html',
    'http://www.ccc.edu/events/Pages/December-2018-Regular-Board-Meeting.aspx'
)
spider = ChiCityCollegeSpider()
item = spider.parse_event_page(test_response)
freezer.stop()


def test_name():
    assert item['name'] == 'Board of Trustees: December 2018 Regular Board Meeting'


def test_start_time():
    assert item['start']['time'] == time(9, 0)
    assert item['start']['date'] == date(2018, 12, 6)
    assert item['start']['note'] is None


def test_end_time():
    assert item['end']['time'] == time(12, 0)
    assert item['end']['date'] == date(2018, 12, 6)
    assert item['end']['note'] is None


def test_id():
    assert item[
        'id'
    ] == 'chi_city_college/201812060900/x/board_of_trustees_december_2018_regular_board_meeting'


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
    ] == 'The December regularly scheduled meeting of the Board of Trustees of Community College District No. 508, County of Cook and State of Illinois, has been scheduled for Thursday, December 6, 2018 at 9:00 a.m., Harold Washington College, 30 E. Lake Street, 11th Floor, Chicago, IL 60601. Any individual planning to attend this meeting who will need an accommodation under the Americans with Disabilities Act should notify the Board Office, at (312) 553-2515 or at requesttospeak@ccc.edu.'  # noqa


def test_documents():
    assert item['documents'] == [{
        'note': 'Agenda',
        'url': 'http://www.ccc.edu/events/Documents/DECEMBER AGENDA.pdf'
    }]


def test__type():
    assert item['_type'] == 'event'
