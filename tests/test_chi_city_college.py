from tests.utils import file_response
from documenters_aggregator.spiders.chi_city_college import Chi_cityCollegeSpider


test_response = file_response('files/ccc_event.html')
spider = Chi_cityCollegeSpider()
item = spider.parse_event_page(test_response)


def test_name():
    assert item['name'] == 'November 2017 Regular Board Meeting'


def test_start_time():
    assert item['start_time'].isoformat() == '2017-11-02T09:00:00-05:00'


def test_end_time():
    assert item['end_time'] is None


def test_id():
    assert item['id'] == 'chi_city_college/201711020900/x/november_2017_regular_board_meeting'


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == 'Not classified'


def test_status():
    assert item['status'] == 'tentative'


def test_location():
    assert item['location'] == {
        'url': None,
        'name': None,
        'address': '226 West Jackson Boulevard',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test__type():
    assert item['_type'] == 'event'


def test_timezone():
    assert item['timezone'] == 'America/Chicago'
