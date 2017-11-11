from tests.utils import file_response
from documenters_aggregator.spiders.cook_county import Cook_countySpider


test_response = file_response('files/cook_county_event.html')
spider = Cook_countySpider()
item = spider._parse_event(test_response)


def test_name():
    assert item['name'] == 'ZBA Public Hearing'


def test_start_time():
    assert item['start_time'] == '2017-11-15T13:00:00-06:00'


def test_end_time():
    assert item['end_time'] == '2017-11-15T15:00:00-06:00'


def test_id():
    assert item['id'] == 'ZBAPublicHearing2017-11-15T13:00:00-06:00'


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == 'Public Forum'


def test_status():
    assert item['status'] == 'tentative'


def test_location():
    assert item['location'] == {
        'url': None,
        'name': '69 W. Washington Street Chicago , IL  60602',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test__type():
    assert item['_type'] == 'event'
