import pytest

from tests.utils import file_response
from city_scrapers.spiders.old_town import OldTownSpider
from freezegun import freeze_time
from datetime import date, time

freezer = freeze_time('2018-12-08')
freezer.start()


#def test_tests():
#    print('Please write some tests for this spider or at least disable this one.')
#    assert False


"""
Uncomment below
"""

test_response = file_response('files/old_town.html')
spider = OldTownSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Regular Commission Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2018, 1, 10), 'time': time(17, 30), 'note': ''}


def test_end():
    assert parsed_items[0]['end'] == {'date': date(2018, 1, 10), 'time': time(19, 30), 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'old_town/201801101730/x/regular_commission_meeting'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Near North Branch Public Library',
        'address': '(310 W. Division Street)'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': '',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [{
      'url': 'https://oldtownchicago.org/wp-content/uploads/2018/08/2018-SSA-48-Commission-Minutes-1.10.2018.docx',
      'note': 'minutes'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Commission'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
