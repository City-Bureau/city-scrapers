import pytest
from datetime import date

from tests.utils import file_response
from documenters_aggregator.spiders.ward_night import WardNightSpider, Calendar

test_response = file_response('files/ward_night.json')
spider = WardNightSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_id():
    assert parsed_items[0]['id'] == 'ward1-2017-01-01'


def test_name():
    assert parsed_items[0]['name'] == 'Ward Night with Alderman Joe Moreno (Ward 1)'


def test_description():
    assert parsed_items[0]['description'] == 'first come first served, one-on-one meetings usually about 10-20 minutes'


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-10-30T16:00:00-05:00'


def test_end_time():
    assert parsed_items[0]['end_time'] == '2017-10-30T18:00:00-05:00'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': None,
        'name': '2740 W North Ave, Chicago',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert parsed_items[0]['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert parsed_items[0]['classification'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert parsed_items[0]['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'


# Calendar tests

def test_third_thursday():
    cal = Calendar(date(2017, 10, 15))
    days = cal.nth_weekday(3, 'thursday', 4)

    assert days == [date(2017, 10, 19), date(2017, 11, 16), date(2017, 12, 21),
                    date(2018, 1, 18)]


def test_every_monday():
    cal = Calendar(date(2017, 10, 15))
    days = cal.weekday('monday', 4)

    assert days == [date(2017, 10, 16), date(2017, 10, 23), date(2017, 10, 30),
                    date(2017, 11, 6)]


def test_last_friday():
    cal = Calendar(date(2017, 10, 15))
    days = cal.last_weekday('friday', 4)

    assert days == [date(2017, 10, 27), date(2017, 11, 24), date(2017, 12, 29),
                    date(2018, 1, 26)]
