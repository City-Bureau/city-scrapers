import datetime

import pytest
from tests.utils import file_response

from city_scrapers.spiders.chi_mayors_bicycle_advisory_council import (
    ChiMayorsBicycleAdvisoryCouncilSpider
)

test_response = file_response('files/chi_mayors_bicycle_advisory_council.html')
spider = ChiMayorsBicycleAdvisoryCouncilSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == "Mayor's Bicycle Advisory Council"


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['event_description'] == 'MBAC focuses on a wide range of ' + \
        'bicycle issues: safety, education, enforcement, and ' + \
        'infrastructure investment. The Council will help identify issues, ' + \
        'discuss ideas and set priorities for bicycle planning in Chicago.'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': datetime.date(2018, 3, 7),
        'time': datetime.time(15, 0),
        'note': 'Start at 3 p.m. unless otherwise noted'
    }


def test_end():
    assert parsed_items[0]['end'] == {'date': datetime.date(2018, 3, 7), 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0][
        'id'
    ] == 'chi_mayors_bicycle_advisory_council/201803071500/x/mayor_s_bicycle_advisory_council'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'address': '121 N LaSalle Dr, Chicago, IL',
        'name': 'City Hall, Room 1103',
        'neighborhood': 'Loop',
    }


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    listing_page = {'url': spider.BASE_URL, 'note': ''}
    archive_page = {'url': spider.BASE_URL + 'mbac-meeting-archives/', 'note': 'documents'}
    assert item['sources'] == [listing_page, archive_page]


@pytest.mark.parametrize('item', parsed_items)
def test_documents(item):
    doc_types = ['agenda', 'meeting minutes', 'presentations']

    if item['start']['date'] == datetime.date(2015, 6, 11):
        doc_types.append('d. taylor comments')
    elif item['start']['date'] == datetime.date(2015, 3, 12):
        doc_types.remove('presentations')
    elif item['start']['date'] == datetime.date(2018, 12, 12):
        doc_types = []

    assert [d['note'] for d in item['documents']] == doc_types


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Advisory Committee'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
