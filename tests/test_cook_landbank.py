from datetime import datetime

from city_scrapers_core.constants import COMMITTEE, TENTATIVE
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.cook_landbank import CookLandbankSpider

freezer = freeze_time('2018-09-13 12:00:00')
freezer.start()

test_response = file_response('files/cook_landbank.json')
spider = CookLandbankSpider()
parsed_items = list(spider.parse(test_response))

freezer.stop()


def test_title():
    assert parsed_items[0]['title'] == 'CCLBA Land Transactions Committee'


def test_description():
    assert parsed_items[0]['description'] == (
        'The Land Transactions Committee will convene on Friday, September '
        '14th at the hour of 10:00 AM at the location of 69 W. Washington '
        'St., 22nd Floor, Conference Room ‘B”, Chicago, Illinois, to consider '
        'the following:'
    )


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 9, 14, 10)


def test_end():
    assert parsed_items[0]['end'] is None


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == COMMITTEE


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE


def test_location():
    assert parsed_items[0]['location'] == {
        'name': '',
        'address': '69 W. Washington St., Lower Level Conference Room A Chicago, IL',
    }


def test_sources():
    assert parsed_items[0]['source'] == (
        'http://www.cookcountylandbank.org/events/'
        'cclba-land-transactions-committee-09142018/'
    )


def test_links():
    assert parsed_items[0]['links'] == [{
        'href': (
            'http://www.cookcountylandbank.org/wp-content/'
            'uploads/2018/09/CCLBA-Land-Transaction-9-14-18-Agenda.pdf'
        ),
        'title': 'Agenda'
    }]
