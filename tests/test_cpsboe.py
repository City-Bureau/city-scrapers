# -*- coding: utf-8 -*-
import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.cpsboe import CpsboeSpider

test_response = file_response('files/cpsboe.html')
spider = CpsboeSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

assert len(parsed_items) == 14

@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] == 'event'

def test_id():
    assert parsed_items[0]['id'] == '20170726'