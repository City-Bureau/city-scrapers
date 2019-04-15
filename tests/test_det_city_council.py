from datetime import datetime

import pytest  # noqa
from city_scrapers_core.constants import COMMITTEE, TENTATIVE
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.det_city_council import DetCityCouncilSpider

freezer = freeze_time('2019-02-22')
freezer.start()

test_response = file_response(
    'files/det_city_council.html',
    url='https://detroitmi.gov/events/public-health-and-safety-standing-committee-02-25-19'
)
spider = DetCityCouncilSpider()
item = spider.parse_event_page(test_response)

freezer.stop()


def test_title():
    assert item['title'] == 'Public Health and Safety Standing Committee'


def test_description():
    assert item['description'] == ''


def test_start():
    assert item['start'] == datetime(2019, 2, 25, 10, 0)


def test_end():
    assert item['end'] == datetime(2019, 2, 25, 13, 0)


def test_time_notes():
    assert item['time_notes'] == 'Estimated 3 hour duration'


def test_id():
    assert item['id'
                ] == 'det_city_council/201902251000/x/public_health_and_safety_standing_committee'


def test_status():
    assert item['status'] == TENTATIVE


def test_location():
    assert item['location'] == {
        'name': 'Committee of the Whole Room',
        'address': '2 Woodward Avenue, Suite 1300 Detroit, MI 48226'
    }


def test_source():
    assert item[
        'source'
    ] == 'https://detroitmi.gov/events/public-health-and-safety-standing-committee-02-25-19'


def test_links():
    assert item['links'] == [{
        'href':
            'https://detroitmi.gov/sites/detroitmi.localhost/files/events/2019-02/cal%202-25-19%20PHS.pdf',  # noqa
        'title': 'cal 2-25-19 PHS.pdf'
    }]


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == COMMITTEE
