import pytest
from datetime import date, time


from tests.utils import file_response
from city_scrapers.spiders.det_entertainment_commission import DetEntertainmentCommissionSpider


test_response = file_response('files/det_entertainment_commission.html', 'https://www.detroitsentertainmentcommission.com/services')
spider = DetEntertainmentCommissionSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Entertainment Commission'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 7, 16),
        'time': time(17, 00),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None,
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_entertainment_commission/201807161700/x/entertainment_commission'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Coleman A. Young Municipal Center',
        'address': '2 Woodward Avenue, Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.detroitsentertainmentcommission.com/services',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Commission'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
