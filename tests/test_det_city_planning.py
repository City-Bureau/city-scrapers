from datetime import datetime

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.det_city_planning import DetCityPlanningSpider

freezer = freeze_time('2019-02-22')
freezer.start()

test_response = file_response(
    'files/det_city_planning.html',
    url='https://detroitmi.gov/events/city-planning-commission-meeting-0'
)
spider = DetCityPlanningSpider()
item = spider.parse_event_page(test_response)

freezer.stop()


def test_title():
    assert item['title'] == 'City Planning Commission'


def test_description():
    assert item['description'] == ''


def test_start():
    assert item['start'] == datetime(2019, 1, 17, 16, 45)


def test_end():
    assert item['end'] == datetime(2019, 1, 17, 19, 45)


def test_time_notes():
    assert item['time_notes'] == 'Estimated 3 hour duration'


def test_id():
    assert item['id'] == 'det_city_planning/201901171645/x/city_planning_commission'


def test_status():
    assert item['status'] == PASSED


def test_location():
    assert item['location'] == {
        'name': 'Committee of the Whole Room',
        'address': '2 Woodward Avenue, Suite 1300 Detroit, MI 48226'
    }


def test_source():
    assert item['source'
                ] == 'https://detroitmi.gov/events/city-planning-commission-meeting-0'  # noqa


def test_links():
    assert item['links'] == [
        {
            'href':
                'https://detroitmi.gov/sites/detroitmi.localhost/files/events/2019-01/January%2017%2C%202019%20agenda.pdf',  # noqa
            'title': 'January 17, 2019 agenda.pdf'
        },
        {
            'href':
                'https://detroitmi.gov/sites/detroitmi.localhost/files/events/2019-01/PH%202019-01-17%20515PM.pdf',  # noqa
            'title': 'PH 2019-01-17 515PM.pdf'
        },
        {
            'href':
                'https://detroitmi.gov/sites/detroitmi.localhost/files/events/2019-01/PH%202019-01-17%20600%20PM.pdf',  # noqa
            'title': 'PH 2019-01-17 600 PM.pdf'
        },
    ]


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == COMMISSION
