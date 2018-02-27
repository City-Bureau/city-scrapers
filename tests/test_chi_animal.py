import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.chi_animal import Chi_animalSpider


test_response = file_response('files/chi_animal.html', url='https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html')
spider = Chi_animalSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_len():
    assert len(parsed_items) == 3


def test_name():
    assert parsed_items[0]['name'] == 'Commission meeting'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-09-21T00:00:00-05:00'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html',
                                'note': ''}]


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
