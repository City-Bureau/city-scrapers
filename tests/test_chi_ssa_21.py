from datetime import datetime

import pytest
from city_scrapers_core.constants import COMMISSION
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.chi_ssa_21 import ChiSsa21Spider

freezer = freeze_time('2018-12-07')
freezer.start()

test_response = file_response('files/chi_ssa_21.html')
spider = ChiSsa21Spider()
parsed_items = [item for item in spider.parse(test_response)]


def test_title():
    assert parsed_items[0]['title'] == 'Lincoln Square Neighborhood Improvement Program'


def test_description():
    assert parsed_items[0]['description'] == (
        '2018 Meetings Calendar: Review and Approval\n'
        '2018 Budget Adjustments: (if applicable)\nStrategic Planning: with PLACE Consulting'
    )


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 29, 9)


def test_end():
    assert parsed_items[0]['end'] is None


def test_time_notes():
    assert parsed_items[0]['time_notes'] == 'Estimated 2 hour duration'


def test_id():
    assert parsed_items[0][
        'id'] == 'chi_ssa_21/201801290900/x/lincoln_square_neighborhood_improvement_program'


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'Carbon Arc Bar & Board',
        'address': '4620 N Lincoln Ave, Chicago, IL'
    }


def test_links():
    assert parsed_items[0]['links'] == [{
        'title': 'Minutes',
        'href': (
            'https://chambermaster.blob.core.windows.net/' +
            'userfiles/UserFiles/chambers/697/CMS/SSA_2018/' + 'SSA21_MeetingMinutes_1.29.18.pdf'
        )
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is COMMISSION
