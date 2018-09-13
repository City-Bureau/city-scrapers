from datetime import date, time

import pytest

from tests.utils import file_response
from city_scrapers.constants import FORUM
from city_scrapers.spiders.chi_school_actions import ChiSchoolActionsSpider

test_response = file_response('files/chi_school_actions.html')
spider = ChiSchoolActionsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Castellanos - Cardenas Community Meetings: Consolidation'


def test_description():
    assert parsed_items[3]['event_description'] == 'Emil G Hirsch Metropolitan High School Community Meetings: Co-location'


def test_classification():
    assert parsed_items[0]['classification'] == FORUM


def test_start():
    expected_start = {
        'date': date(2018, 1, 9),
        'time': time(18, 00),
        'note': ''
    }
    assert parsed_items[0]['start'] == expected_start


def test_end():
    expected_end = {
        'date': date(2018, 1, 9),
        'time': time(20, 00),
        'note': ''
    }
    assert parsed_items[0]['end'] == expected_end


def test_id():
    assert parsed_items[0]['id'] == \
           'chi_school_actions/201801091800/x/castellanos_cardenas_community_meetings_consolidation'


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'Rosario Castellanos ES',
        'address': '2524 S Central Park Ave Chicago, IL',
        'neighborhood': '',
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://schoolinfo.cps.edu/SchoolActions/Documentation.aspx',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {'note': 'Transition Plan', 'url': 'http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=5247'},
        {'note': 'Transition Plan - ELL', 'url': 'http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=5248'},
        {'note': 'Parent Letter', 'url': 'http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=5243'},
        {'note': 'Parent Letter - ELL', 'url': 'http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=6298'},
        {'note': 'Staff Letter', 'url': 'http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=5245'},
        {'note': 'Staff Letter - ELL', 'url': 'http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=6306'}
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
