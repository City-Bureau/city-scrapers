import pytest

from freezegun import freeze_time
from tests.utils import file_response
from documenters_aggregator.spiders.parkdistrict import ParkdistrictSpider


freezer = freeze_time('2017-10-10 12:00:01')
freezer.start()
test_response = file_response('files/parkdistrict.html')
spider = ParkdistrictSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Board of Commissioners'
    assert parsed_items[1]['name'] == 'Public Hearing'
    assert parsed_items[3]['name'] == 'Special Meeting'
    assert parsed_items[6]['name'] == 'Budget Forum'


def test_description():
    assert parsed_items[0]['description'] == 'Not available'


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-12-13T15:30:00-06:00'


def test_id():
    assert parsed_items[0]['id'] == 'BoardofCommissioners12132017'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert parsed_items[0]['status'] == 'tentative'
    assert parsed_items[1]['status'] == 'tentative'
    assert parsed_items[2]['status'] == 'tentative'
    assert parsed_items[3]['status'] == 'confirmed'
    assert parsed_items[4]['status'] == 'confirmed'
    assert parsed_items[5]['status'] == 'passed'
    assert parsed_items[6]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': None,
        'name': '8TH FLOOR BOARD ROOM\n--em--ADMINISTRATION BUILDING AT 541 NORTH FAIRBANKS COURT, \r\nCHICAGO, ILLINOIS 60611 \r\n8TH FLOOR BOARD ROOM--em--',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
