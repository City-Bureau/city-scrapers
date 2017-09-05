# -*- coding: utf-8 -*-
import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.cpsboe import CpsboeSpider

test_response = file_response('files/cpsboe.html')
spider = CpsboeSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_event_count():
    assert len(parsed_items) == 14


@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] == 'event'


def test_id():
    assert parsed_items[0]['id'] == '201707261030'


@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == 'Chicago Board of Education Monthly Meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == """CPS Loop Office
42 W. Madison Street, Garden Level
Chicago, IL 60602
Board Room"""


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'


def test_start_time():
    assert parsed_items[0]['start_time'] == "2017-07-26T10:30:00-05:00"


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'url': '',
        'name': 'See description',
        'coordinates': None,
    }
