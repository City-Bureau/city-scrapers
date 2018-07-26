import pytest
from datetime import date, time

from tests.utils import file_response
from city_scrapers.spiders.det_land_bank import Det_land_bankSpider


test_response = file_response('files/det_land_bank.html', 'https://buildingdetroit.org/events/meetings')
spider = Det_land_bankSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board of Directors Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == 'Meeting'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2017, 10, 17),
        'time': time(13, 0),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {'date': None, 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'det_land_bank/201710171300/x/board_of_directors_meeting'


# def test_status():
    # assert parsed_items[0]['status'] == 'EXPECTED STATUS'


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
      'url': 'https://s3.us-east-2.amazonaws.com/dlba-production-bucket/Meetings/documents/01152018103044.pdf',
      'note': ''
    }]


# @pytest.mark.parametrize('item', parsed_items)
# def test_all_day(item):
    # assert item['all_day'] is False


# @pytest.mark.parametrize('item', parsed_items)
# def test_classification(item):
    # assert item['classification'] is None


# @pytest.mark.parametrize('item', parsed_items)
# def test__type(item):
    # assert parsed_items[0]['_type'] == 'event'
