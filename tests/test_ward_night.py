import pytest
from datetime import date

from tests.utils import file_response
from documenters_aggregator.spiders.ward_night import WardNightSpider, Calendar

test_response = file_response('files/ward_night.json')
spider = WardNightSpider(start_date=date(2017, 11, 1))
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_id():
    assert parsed_items[0]['id'] == 'ward1-2017-11-07'


def test_name():
    assert parsed_items[0]['name'] == 'Ward Night with Alderman Joe Moreno (Ward 1)'


def test_description():
    assert parsed_items[0]['description'] == 'first come first served, one-on-one meetings usually about 10-20 minutes'


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-11-07T16:00:00-06:00'


def test_end_time():
    assert parsed_items[0]['end_time'] == '2017-11-07T18:00:00-06:00'


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


# Test integration with the Calendar class

def test_weekly_generation():
    row = [
        'Gregory Mitchell',
        '773.731.7777',
        'https://www.gregmitchell7thward.org/',
        '7',
        'Bridget Newsham',
        'Yes',
        '2249 E 95th St. Chicago ',
        'Weekly',
        'Monday',
        '3:00 PM',
        '7:00 PM',
        'No',
        '',
        'First come first served '
    ]

    spider = WardNightSpider()
    events = spider._parse_row(row)

    assert events[0]['start_time'] == '2017-11-06T15:00:00-06:00'
    assert events[0]['end_time'] == '2017-11-06T19:00:00-06:00'
    assert events[0]['id'] == 'ward7-2017-11-06'

    assert events[1]['start_time'] == '2017-11-13T15:00:00-06:00'
    assert events[1]['end_time'] == '2017-11-13T19:00:00-06:00'
    assert events[1]['id'] == 'ward7-2017-11-13'

    assert events[2]['start_time'] == '2017-11-20T15:00:00-06:00'
    assert events[2]['end_time'] == '2017-11-20T19:00:00-06:00'
    assert events[2]['id'] == 'ward7-2017-11-20'


def test_monthly_generation():
    row = [
        'Leslie Hairston',
        '773.324.5555',
        'http://leslieahairston.com/',
        '5',
        'Bridget Newsham',
        'Yes',
        'Rotating locations',
        'Monthly (4th occurrence)',
        'Tuesday',
        '6:00 PM',
        '8:00 PM',
        '',
        '',
        'Every fourth Tuesday, no meeting in November or December, group meetings rather than one-on-one'
    ]

    spider = WardNightSpider()
    events = spider._parse_row(row)

    assert events[0]['start_time'] == '2017-11-28T18:00:00-06:00'
    assert events[0]['end_time'] == '2017-11-28T20:00:00-06:00'
    assert events[0]['id'] == 'ward5-2017-11-28'

    assert events[1]['start_time'] == '2017-12-26T18:00:00-06:00'
    assert events[1]['end_time'] == '2017-12-26T20:00:00-06:00'
    assert events[1]['id'] == 'ward5-2017-12-26'

    assert events[2]['start_time'] == '2018-01-23T18:00:00-06:00'
    assert events[2]['end_time'] == '2018-01-23T20:00:00-06:00'
    assert events[2]['id'] == 'ward5-2018-01-23'


# Calendar tests

def test_third_thursday():
    cal = Calendar(date(2017, 10, 15))
    days = cal.nth_weekday(3, 'Thursday', 4)

    assert days == [date(2017, 10, 19), date(2017, 11, 16), date(2017, 12, 21),
                    date(2018, 1, 18)]


def test_every_monday():
    cal = Calendar(date(2017, 10, 15))
    days = cal.weekday('Monday', 4)

    assert days == [date(2017, 10, 16), date(2017, 10, 23), date(2017, 10, 30),
                    date(2017, 11, 6)]


def test_last_friday():
    cal = Calendar(date(2017, 10, 15))
    days = cal.last_weekday('Friday', 4)

    assert days == [date(2017, 10, 27), date(2017, 11, 24), date(2017, 12, 29),
                    date(2018, 1, 26)]
