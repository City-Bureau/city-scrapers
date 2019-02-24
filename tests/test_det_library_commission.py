from datetime import datetime

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.det_library_commission import DetLibraryCommissionSpider

test_response = file_response(
    'files/det_library_commission.html', 'https://detroitpubliclibrary.org/meeting/4908'
)

spider = DetLibraryCommissionSpider()

freezer = freeze_time('2019-02-24')
freezer.start()
item = spider._parse_item(test_response)
freezer.stop()


def test_title():
    assert item['title'] == 'Regular Commission Meeting'


def test_description():
    assert item['description'] == ''


def test_start():
    assert item['start'] == datetime(2019, 1, 15, 13, 30)


def test_end():
    assert item['end'] == datetime(2019, 1, 15, 14, 30)


def test_time_notes():
    assert item['time_notes'] == ''


def test_id():
    assert item['id'] == 'det_library_commission/201901151330/x/regular_commission_meeting'


def test_status():
    assert item['status'] == PASSED


def test_location():
    assert item['location'] == {
        'name': 'Main',
        'address': '5201 Woodward Ave. Detroit, Michigan 48202 U.S.'
    }


def test_source():
    assert item['source'] == 'https://detroitpubliclibrary.org/meeting/4908'


def test_links():
    assert item['links'] == [{
        'href':
            'https://d2qp1eesgvzzix.cloudfront.net/uploads/files/commission/1-15-19-DETROIT-LIBRARY-COMMISSION-PROCEEDINGS.pdf?mtime=20190219160850',  # noqa
        'title': 'DLC Minutes, January 15, 2019'
    }]


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == COMMISSION
