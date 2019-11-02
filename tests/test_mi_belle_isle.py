from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response

from city_scrapers.spiders.mi_belle_isle import MiBelleIsleSpider

test_response = file_response(
    join(dirname(__file__), "files", "mi_belle_isle.html"),
    url='https://www.michigan.gov/dnr/0,4570,7-350-79137_79763_79901---,00.html',
)
spider = MiBelleIsleSpider()
parsed_items = [item for item in spider.parse(test_response)]
parsed_items = sorted(parsed_items, key=lambda x: x['start'])


def test_title():
    assert parsed_items[0]['title'] == 'Belle Isle Advisory Committee'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 18, 9)


def test_end():
    assert parsed_items[0]['end'] == datetime(2018, 1, 18, 11)


def test_id():
    assert parsed_items[0]['id'] == 'mi_belle_isle/201801180900/x/belle_isle_advisory_committee'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'Flynn Pavilion',
        'address': ('Intersection of Picnic Way and Loiter Way, '
                    'Belle Isle, Detroit, MI 48207'),
    }


def test_sources():
    assert parsed_items[0][
        'source'] == 'https://www.michigan.gov/dnr/0,4570,7-350-79137_79763_79901---,00.html'


def test_links():
    assert parsed_items[0]['links'] == [{
        'title': 'Minutes',
        'href': ('https://www.michigan.gov/documents/'
                 'dnr/BIPAC011818minutes_612208_7.pdf'),
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == ADVISORY_COMMITTEE
