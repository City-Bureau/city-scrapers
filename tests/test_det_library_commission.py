import pytest

from datetime import date, time
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.spiders.det_library_commission import DetLibraryCommissionSpider


test_response = file_response('files/det_library_commission.html', 'https://detroitpubliclibrary.org/about/commission')

spider = DetLibraryCommissionSpider()


def test_request_count():
    requests = list(spider.parse(test_response))
    assert len(requests) == 4


test_detail = file_response(
    'files/det_library_commission_detail.html',
    'https://detroitpubliclibrary.org/meeting/1973'
)


freezer = freeze_time('2018-08-04 12:00:01')
freezer.start()
parsed_items = [item for item in spider._parse_item(test_detail) if isinstance(item, dict)]
parsed_items = sorted(parsed_items, key=lambda x: x['start']['date'])

freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Regular Commission Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2018, 9, 18), 'time': time(13, 30), 'note': ''}


def test_end():
    assert parsed_items[0]['end'] == {'date': date(2018, 9, 18), 'time': time(15, 30), 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'det_library_commission/201809181330/x/regular_commission_meeting'


def test_status():
    assert parsed_items[0]['status'] == 'tentative'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Explorers Room, Main Branch, Detroit Public Library',
        'address': '5201 Woodward Ave. Detroit, Michigan 48202'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://detroitpubliclibrary.org/meeting/1973',
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
