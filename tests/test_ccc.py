from tests.utils import file_response
from documenters_aggregator.spiders.ccc import CccSpider


test_response = file_response('files/ccc_event.html')
spider = CccSpider()
item = spider.parse_event_page(test_response)

def test_name():
    assert item['name'] == 'November 2017 Regular Board Meeting'


def test_start_time():
    assert item['start_time'] == '2017-11-02T09:00:00-05:00'


def test_end_time():
    assert item['end_time'] is None


def test_id():
    assert item['id'] == 'November2017RegularBoardMeeting'


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == 'Not classified'


def test_status():
    assert item['status'] == 'tentative'


def test_location():
    assert item['location'] == {
        'url': None,
        'name': '226 West Jackson Boulevard',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test__type():
    assert item['_type'] == 'event'
