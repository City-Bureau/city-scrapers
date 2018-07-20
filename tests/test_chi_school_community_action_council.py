from datetime import datetime, time, date
import pytest
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.spiders.chi_school_community_action_council import Chi_school_community_action_councilSpider

freezer = freeze_time('2018-06-01 12:00:01')
freezer.start()
test_response = file_response('files/chi_school_community_action_council_CAC.html', url='http://cps.edu/FACE/Pages/CAC.aspx')
spider = Chi_school_community_action_councilSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
current_month_number = datetime.today().month
freezer.stop()


def test_num_items():
    assert len(parsed_items) == (13 - current_month_number)*8


def test_name():
    assert parsed_items[0]['name'] == 'Austin Community Action Council'


def test_start_time():
    EXPECTED_START = {
        'date': date(2018, 6, 12),
        'time': time(17, 30),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START

def test_end_time():
    EXPECTED_END = {
        'date': date(2018, 6, 12),
        'time': time(20, 30),
        'note': 'Estimated 3 hours after the start time'
    }
    assert parsed_items[0]['end'] == EXPECTED_END


def test_id():
    assert parsed_items[0]['id'] == \
           'chi_school_community_action_council/201806121730/x/austin_community_action_council'


def test_location():
    assert parsed_items[0]['location'] == {
            'name': ' Michele Clark HS ',
            'address': '5101 W Harrison St.',
            'neighborhood': 'Austin'
        }


def test_sources():
    EXPECTED_SOURCES = [
        {
            'url': 'http://cps.edu/FACE/Pages/CAC.aspx',
            'note': 'CAC Meetings Website'
        },
        {
            'url': 'https://cacbronzeville.weebly.com/',
            'note': "Neighborhood's Website"
        },
    ]
    assert parsed_items[1]['sources'] == EXPECTED_SOURCES


@pytest.mark.parametrize('item', parsed_items)
def test_documents(item):
    assert item['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'committee'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
