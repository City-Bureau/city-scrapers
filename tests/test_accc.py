import pytest
from datetime import date
from tests.utils import file_response
from documenters_aggregator.spiders.accc import AcccSpider


test_response = file_response('files/accc.html')
spider = AcccSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_len():
    assert len(parsed_items) == 3


def test_name():
    assert parsed_items[0]['name'] == 'Commission meeting'


def test_start_time():
    assert parsed_items[0]['start_time'] == date(2017, 9, 21)
