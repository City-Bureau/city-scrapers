from tests.utils import file_response
from documenters_aggregator.spiders.cook_county import Cook_countySpider


test_response = file_response('files/cook_county_event.html',
                              url='https://www.cookcountyil.gov/event/cook-county-zoning-building-committee-6')
spider = Cook_countySpider()
item = spider._parse_event(test_response)


def test_name():
    assert item['name'] == 'ZBA Public Hearing'


def test_start_time():
    assert item['start_time'].isoformat() == '2017-11-15T13:00:00-06:00'


def test_end_time():
    assert item['end_time'].isoformat() == '2017-11-15T15:00:00-06:00'


def test_id():
    assert item['id'] == 'cook_county/201711151300/x/zba_public_hearing'


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == 'Public Forum'


def test_status():
    assert item['status'] == 'tentative'


def test_location():
    assert item['location'] == {
        'url': None,
        'name': None,
        'address': '69 W. Washington Street Chicago , IL  60602',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test__type():
    assert item['_type'] == 'event'


def test_timezone():
    assert item['timezone'] == 'America/Chicago'


def test_sources():
    assert item['sources'] == [{'url': 'https://www.cookcountyil.gov/event/cook-county-zoning-building-committee-6',
                                'note': ''}]
