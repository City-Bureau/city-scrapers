from datetime import date, time

import pytest
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.spiders.det_board_of_education import DetBoardOfEducationSpider

test_response = file_response('files/det_board_of_education.html', 'http://detroitk12.org/board/meetings/')
freezer = freeze_time('2018-08-15 12:00:01')
freezer.start()
spider = DetBoardOfEducationSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
freezer.stop()


def test_count():
    assert len(parsed_items) == 44


def test_name():
    assert parsed_items[0]['name'] == 'Policy Ad-hoc Sub-Committee Meeting (Open)'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 8, 21), 'time': time(9, 00), 'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 8, 21), 'time': time(10, 30), 'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_board_of_education/201808210900/x/policy_ad_hoc_sub_committee_meeting_open'


def test_status():
    assert parsed_items[0]['status'] == 'confirmed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': '',
        'address': 'Fisher Building, 3011 W. Grand Boulevard, 12th Floor Conference Room'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://detroitk12.org/board/meetings/',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
