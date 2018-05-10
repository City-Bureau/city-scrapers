import pytest

from tests.utils import file_response
from city_scrapers.spiders.cps_community_action_council import Cps_community_action_councilSpider

test_response = file_response('files/cps_community_action_council_CAC.html', url='http://cps.edu/FACE/Pages/CAC.aspx')
spider = Cps_community_action_councilSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_len():
    assert len(parsed_items) == 8


def test_name():
    assert parsed_items[0]['name'] == 'Austin CPS community action council meeting'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2018-05-08T17:30:00'


def test_id():
    assert parsed_items[0]['id'] == \
           'cps_community_action_council/201805081730/x/austin_cps_community_action_council_meeting'


def test_location():
    assert parsed_items[0]['location'] == {
            'url': None,
            'name': 'Austin',
            'address': ' at Michele Clark HS (5101 W Harrison St.)',
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == None

@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end_time'] == None

@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'http://cps.edu/FACE/Pages/CAC.aspx',
                                'note': ''}]

@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Education'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
