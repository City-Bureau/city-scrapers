from datetime import datetime

import pytest  # noqa
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import COMMISSION, TENTATIVE
from city_scrapers.spiders.det_human_rights import DetHumanRightsSpider

freezer = freeze_time('2019-03-18')
freezer.start()

test_response = file_response(
    'files/det_human_rights.html',
    url='https://detroitmi.gov/events/human-rights-commssion-meeting-2',
)
spider = DetHumanRightsSpider()
item = spider.parse_event_page(test_response)

freezer.stop()


def test_title():
    assert item['title'] == 'Human Rights Commission - Meeting'


def test_description():
    assert item['description'] == ''


def test_start():
    assert item['start'] == datetime(2019, 3, 21, 16, 0)


def test_end():
    assert item['end'] == datetime(2019, 3, 21, 17, 0)


def test_time_notes():
    assert item['time_notes'] == ''


def test_id():
    assert item['id'] == 'det_human_rights/201903211600/x/human_rights_commission_meeting'  # noqa


def test_status():
    assert item['status'] == TENTATIVE


def test_location():
    assert item['location'] == {
        'name': 'Coleman A. Young Municipal Center , Room 1240',
        'address': '2 Woodward Ave. Detroit, MI 48226'
    }


def test_source():
    assert item['source'] == 'https://detroitmi.gov/events/human-rights-commssion-meeting-2'


def test_links():
    assert item['links'] == [{
        'href':
            'https://detroitmi.gov/sites/detroitmi.localhost/files/events/2019-03/Meeting%20Notice%203-21-19_0.pdf',  # noqa
        'title': 'Meeting Notice 3-21-19_0.pdf'
    }]


def test_classification():
    assert item['classification'] == COMMISSION


def test_all_day():
    assert item['all_day'] is False
