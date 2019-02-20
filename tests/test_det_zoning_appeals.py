from datetime import date, time

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.det_zoning_appeals import DetZoningAppealsSpider

freezer = freeze_time('2018-12-27')
freezer.start()

test_response = file_response(
    'files/det_zoning_appeals.html',
    'https://www.detroitmi.gov/Government/Boards/Board-of-Zoning-Appeals-Meeting'
)
spider = DetZoningAppealsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
parsed_items = sorted(parsed_items, key=lambda x: (x['start']['date'], x['start']['time']))

freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Board of Zoning Appeals'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2018, 1, 23), 'time': time(9, 0), 'note': ''}


def test_end():
    assert parsed_items[0]['end'] == {'date': date(2018, 1, 23), 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'det_zoning_appeals/201801230900/x/board_of_zoning_appeals'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': '13th Floor in the Auditorium, Coleman A. Young Municipal Center',
        'address': '2 Woodward Avenue, Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.detroitmi.gov/Government/Boards/Board-of-Zoning-Appeals-Meeting',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [{
        'url': 'https://www.detroitmi.gov/document/january-23-2018',
        'note': 'Minutes'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
