from datetime import date, time

import pytest
# Adapted from test_chi_parks.py
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.spiders.wayne_public_services import Wayne_public_servicesSpider


freezer = freeze_time('2018-03-27 12:00:01')
freezer.start()
test_response = file_response(
    'files/wayne_public_services.html', url='https://www.waynecounty.com/elected/commission/public-services.aspx')
spider = Wayne_public_servicesSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
freezer.stop()


# PARAMETRIZED TESTS

@pytest.mark.parametrize('item', parsed_items)
def test_event_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    expected_location = ({
        'name': '7th floor meeting room, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
        'neighborhood': '',
    })
    assert item['location'] == expected_location


@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == 'Wayne County Committee on Public Services'


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end'] == {
        'date': None,
        'time': None,
        'note': '',
    }


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Committee'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{
        'url': 'https://www.waynecounty.com/elected/commission/public-services.aspx',
        'note': ''
    }]


# NON-PARAMETRIZED TESTS
def test_documents():
    assert parsed_items[0]['documents'] == [{
        'note': 'agenda',
        'url': 'https://www.waynecounty.com/documents/commission/copsnotice2018jan17.pdf',
    }]


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 17),
        'time': time(11, 0),
        'note': '',
    }


def test_id():
    assert parsed_items[0]['id'] == 'wayne_public_services/201801171100/x/wayne_county_committee_on_public_services'


def test_status():
    assert parsed_items[0]['status'] == 'passed'
