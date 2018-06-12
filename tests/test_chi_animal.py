import pytest

from tests.utils import file_response
from city_scrapers.spiders.chi_animal import Chi_animalSpider


test_response = file_response('files/chi_animal.html', url='https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html')
spider = Chi_animalSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_len():
    assert len(parsed_items) == 3

# Different that last static pull
# def test_id():
#    assert parsed_items[0]['id'] == 'chi_animal/201709210000/x/commission_meeting'

def test_name():
    assert parsed_items[0]['name'] == 'Commission meeting'

# Different than last static pull
def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-09-21T00:00:00-05:00'


@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] == 'event'

@pytest.mark.parametrize('item', parsed_items)
def test_allday(item):
    assert item['all_day'] == False

@pytest.mark.parametrize('item', parsed_items)
def test_class(item):
    assert item['classification'] == 'Not classified'

@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == 'Commission meeting'

@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] is None

@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end_time'] is None

@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {'address': '2741 S. Western Ave, Chicago, IL 60608',
    'coordinates': {'latitude': None, 'longitude': None},
    'name': 'David R. Lee Animal Care Center',
    'url': None}

@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'

@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html',
                                'note': ''}]

@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
