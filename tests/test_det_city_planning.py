import pytest
from datetime import date, time


from tests.utils import file_response
from city_scrapers.constants import COMMISSION
from city_scrapers.spiders.det_city_planning import DetCityPlanningSpider


test_response = file_response('files/det_city_planning.html', url='https://www.detroitmi.gov/Government/Boards/City-Planning-Commission-Meetings')
spider = DetCityPlanningSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
parsed_items = sorted(parsed_items, key=lambda x: x['start']['date'])


def test_name():
    assert parsed_items[0]['name'] == 'City Planning Commission Regular Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2017, 6, 1), 'time': time(17, 0), 'note': 'Meeting runs from 5:00 pm to approximately 8:00 pm'}


def test_end():
    assert parsed_items[0]['end'] == {'date': date(2017, 6, 1), 'time': time(20, 0), 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'det_city_planning/201706011700/x/city_planning_commission_regular_meeting'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Committee of the Whole Room, 13th floor, Coleman A. Young Municipal Center',
        'address': '2 Woodward Avenue, Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.detroitmi.gov/Government/Boards/City-Planning-Commission-Meetings',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [{
      'url': 'https://www.detroitmi.gov/LinkClick.aspx?fileticket=Cuo4pTDuxak%3d&portalid=0',
      'note': 'Agenda'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is COMMISSION


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
