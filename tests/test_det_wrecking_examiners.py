import pytest
import datetime
from tests.utils import file_response
from city_scrapers.spiders.det_wrecking_examiners import DetWreckingExaminersSpider


test_response = file_response('files/det_wrecking_examiners.html', 'https://www.detroitmi.gov/government/boards/board-wrecking-contractors-examiners/board-wrecking-contractors-meetings')
spider = DetWreckingExaminersSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board of Wrecking Contractors Examiners'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {'date': datetime.date(2018, 2, 14), 'time': datetime.time(13, 0), 'note': ''}


def test_end():
    assert parsed_items[0]['end'] == {'date': None, 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'det_wrecking_examiners/201802141300/x/board_of_wrecking_contractors_examiners'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Coleman A. Young Municipal Center, Room 412',
        'address': '2 Woodward Avenue, Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.detroitmi.gov/government/boards/board-wrecking-contractors-examiners/board-wrecking-contractors-meetings',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
