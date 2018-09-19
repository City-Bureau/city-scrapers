import pytest

from tests.utils import file_response
from city_scrapers.constants import ADVISORY_COMMITTEE
from city_scrapers.spiders.chi_animal import ChiAnimalSpider


test_response = file_response('files/chi_animal.html', url='https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html')
spider = ChiAnimalSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_len():
    assert len(parsed_items) == 3

# Different that last static pull
# def test_id():
#    assert parsed_items[0]['id'] == 'chi_animal/201709210000/x/commission_meeting'

# Different than last static pull
def test_start_time():
    assert parsed_items[0]['start']['date'].isoformat() == '2017-09-21'
    assert parsed_items[0]['start']['time'].isoformat() == '00:00:00'

def test_end_time():
    assert parsed_items[0]['end']['date'].isoformat() == '2017-09-21'
    assert parsed_items[0]['end']['time'].isoformat() == '03:00:00'
    assert parsed_items[0]['end']['note'] == (
        'estimated 3 hours after the start time')

@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] == 'event'

@pytest.mark.parametrize('item', parsed_items)
def test_allday(item):
    assert item['all_day'] == False

@pytest.mark.parametrize('item', parsed_items)
def test_class(item):
    assert item['classification'] == ADVISORY_COMMITTEE

@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == 'Advisory Board'

@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert 'description' not in item

@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {'address': '2741 S. Western Ave, Chicago, IL 60608',
    'name': 'David R. Lee Animal Care Center'}

@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'passed'

@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html',
                                'note': ''}]

@pytest.mark.parametrize('item', parsed_items)
def test_documents(item):
    assert len(item['documents']) == 2
