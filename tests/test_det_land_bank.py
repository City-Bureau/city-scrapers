import pytest
from datetime import date, time

from tests.utils import file_response
from city_scrapers.spiders.det_land_bank import DetLandBankSpider


test_response = file_response('files/det_land_bank.html', 'https://buildingdetroit.org/events/meetings')
spider = DetLandBankSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
parsed_items = sorted(parsed_items, key=lambda x: (x['start']['date'], x['start']['time']))


def test_name():
    assert parsed_items[0]['name'] == 'Board Of Director Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2014, 1, 21),
        'time': time(14, 0),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {'date': None, 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'det_land_bank/201401211400/x/board_of_director_meeting'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': '',
        'address': '500 Griswold  Street, Suite 1200 Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://buildingdetroit.org/events/meetings',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [{
      'url': 'https://s3.us-east-2.amazonaws.com/dlba-production-bucket/Meetings/documents/01172018085612.pdf',
      'note': 'minutes'
    }]


def test_classification():
    assert parsed_items[0]['classification'] == 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
