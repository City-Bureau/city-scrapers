from datetime import date, time

from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import BOARD, COMMITTEE, TENTATIVE
from city_scrapers.spiders.chi_city_college import ChiCityCollegeSpider

freezer = freeze_time('2018-01-12')
freezer.start()
test_response = file_response(
    'files/chi_city_college.html',
    'http://www.ccc.edu/events/Pages/March-2019-Board-and-Committee-Meetings.aspx'
)
spider = ChiCityCollegeSpider()
parsed_items = [item for item in spider.parse_event_page(test_response) if isinstance(item, dict)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Committee on Finance and Administrative Services'
    assert parsed_items[1]['name'] == 'Board of Trustees'


def test_start_time():
    assert parsed_items[0]['start']['time'] == time(12, 0)
    assert parsed_items[0]['start']['date'] == date(2019, 2, 7)
    assert parsed_items[0]['start']['note'] is None


def test_end_time():
    assert parsed_items[0]['end']['time'] == time(14, 0)
    assert parsed_items[0]['end']['date'] == date(2019, 2, 7)
    assert parsed_items[0]['end']['note'] == 'Estimated 2 hours after start time'


def test_id():
    assert parsed_items[0][
        'id'] == 'chi_city_college/201902071200/x/committee_on_finance_and_administrative_services'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == COMMITTEE
    assert parsed_items[1]['classification'] == BOARD


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'Harold Washington College',
        'address': '30 E. Lake Street Chicago, IL 60601',
        'neighborhood': None,
    }


def test_description():
    assert parsed_items[0][
        'event_description'
    ] == 'The Board of Trustees of Community College District No. 508, County of Cook and State of Illinois will hold the following meetings on Thursday, February 7, 2019 at Harold Washington College, 30 East Lake Street, 11th Floor, Room 1115, Chicago, Illinois 60601. Any individual planning to attend these meetings and who will need an accommodation under the Americans with Disabilities Act should notify the Board Office, at (312) 553-2515 or at requesttospeak@ccc.edu.'  # noqa


def test_documents():
    assert parsed_items[0]['documents'] == []


def test__type():
    assert parsed_items[0]['_type'] == 'event'
