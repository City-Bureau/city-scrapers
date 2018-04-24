## Framework copied from test_ward_night to update

import pytest
from datetime import date
from datetime import datetime
from pytz import timezone

from tests.utils import file_response
from documenters_aggregator.spiders.chi_localschoolcouncil import chi_LSCMeetingSpider
from textwrap import dedent

test_response = file_response('files/tests_chilocal_events.json')
spider = chi_LSCMeetingSpider(start_date=datetime(2018, 1, 1))
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_id():
    assert parsed_items[0]['id'] == 'chi_localschoolcouncil/201801081600/x/local_school_council_fort_dearborn_es'


def test_name():
    assert parsed_items[0]['name'] == 'Local School Council: Fort Dearborn ES'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2018-01-08T16:00:00-06:00'


def test_end_time():
    assert parsed_items[0]['end_time'] == None


def test_location():
    assert parsed_items[0]['location'] == {
        'address': '9025 S Throop St 60620',
        'coordinates': {
            'latitude': '41.72967267',
            'longitude': '-87.65548116',
        }
    }


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'

