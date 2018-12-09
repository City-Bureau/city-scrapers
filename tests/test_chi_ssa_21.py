import pytest
from tests.utils import file_response
from datetime import time, date
from freezegun import freeze_time

from city_scrapers.constants import COMMISSION
from city_scrapers.spiders.chi_ssa_21 import ChiSsa21Spider

freezer = freeze_time('2018-12-07')
freezer.start()

test_response = file_response('files/chi_ssa_21.html')
spider = ChiSsa21Spider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Lincoln Square Neighborhood Improvement Program'


def test_description():
    assert parsed_items[0]['event_description'] == (
        '2018 Meetings Calendar: Review and Approval\n' +
        '2018 Budget Adjustments: (if applicable)\n' +
        'Strategic Planning: with PLACE Consulting'
    )


def test_start():
    assert parsed_items[0]['start'] == {
        'time': time(9, 0),
        'date': date(2018, 1, 29),
        'note': None
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'time': time(11, 0),
        'date': date(2018, 1, 29),
        'note': 'estimated 2 hours after start time'
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_ssa_21/201801290900/x/lincoln_square_neighborhood_improvement_program'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Carbon Arc Bar & Board',
        'address': '4620 N Lincoln Ave, Chicago, IL'
    }


def test_documents():
    assert parsed_items[0]['documents'] == [{
        'note': 'Minutes',
        'url': (
            'https://chambermaster.blob.core.windows.net/' +
            'userfiles/UserFiles/chambers/697/CMS/SSA_2018/' +
            'SSA21_MeetingMinutes_1.29.18.pdf'
        )
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is COMMISSION


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
