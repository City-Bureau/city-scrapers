import pytest
from datetime import date, time

from tests.utils import file_response
from city_scrapers.spiders.chi_ward_night import ChiWardNightSpider, Calendar

test_response = file_response('files/test_chi_ward_night.json')
spider = ChiWardNightSpider(start_date=date(2017, 11, 1))
parsed_items = [
    item for item in spider.parse(test_response) if isinstance(item, dict)
]


def test_id():
    assert parsed_items[0]['id'] == (
        'chi_ward_night/201711071600/x/ward_night_ward_1'
    )


def test_name():
    assert parsed_items[0]['name'] == 'Ward Night: Ward 1'


def test_event_description():
    assert parsed_items[0]['event_description'] == (
        'Ward Night with Ald. Joe Moreno (Ward 1)\n\n'
        'Frequency: Weekly\n'
        'Day of the Week: Tuesday\n'
        'Requires Sign-Up: No\n'
        'Phone: 773.278.0101\n'
        'Email: ward01@cityofchicago.org\n'
        'Website: https://www.aldermanmoreno.com/\n'
        'Notes: first come first served, one-on-one meetings usually about 10-20 minutes'
    )


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2017, 11, 7),
        'time': time(16, 00)
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2017, 11, 7),
        'time': time(18, 00)
    }


def test_location():
    assert parsed_items[0]['location'] == {
        'name': '',
        'address': '2740 W North Ave, Chicago IL',
        'neighborhood': ''
    }


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'City Council'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'passed'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_documents(item):
    assert item['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == []


# Test integration with the Calendar class

def test_weekly_generation():
    row = [
        'Gregory Mitchell',
        '773.731.7777',
        'test@example.com',
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

    spider = ChiWardNightSpider()
    spider.start_date = date(2017, 10, 31)
    events = spider._parse_row(row)

    assert events[0]['start'] == {
        'date': date(2017, 11, 6),
        'time': time(15, 00),
    }
    assert events[0]['end'] == {
        'date': date(2017, 11, 6),
        'time': time(19, 00)
    }
    assert events[0]['id'] == 'chi_ward_night/201711061500/x/ward_night_ward_7'

    assert events[1]['start'] == {
        'date': date(2017, 11, 13),
        'time': time(15, 00),
    }
    assert events[1]['end'] == {
        'date': date(2017, 11, 13),
        'time': time(19, 00)
    }
    assert events[1]['id'] == 'chi_ward_night/201711131500/x/ward_night_ward_7'

    assert events[2]['start'] == {
        'date': date(2017, 11, 20),
        'time': time(15, 00),
    }
    assert events[2]['end'] == {
        'date': date(2017, 11, 20),
        'time': time(19, 00)
    }
    assert events[2]['id'] == 'chi_ward_night/201711201500/x/ward_night_ward_7'


def test_monthly_generation():
    row = [
        'Leslie Hairston',
        '773.324.5555',
        'test@example.com',
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

    spider = ChiWardNightSpider()
    spider.start_date = date(2017, 10, 31)
    events = spider._parse_row(row)

    assert events[0]['start'] == {
        'date': date(2017, 11, 28),
        'time': time(18, 00)
    }
    assert events[0]['end'] == {
        'date': date(2017, 11, 28),
        'time': time(20, 00)
    }
    assert events[0]['id'] == 'chi_ward_night/201711281800/x/ward_night_ward_5'

    assert events[1]['start'] == {
        'date': date(2017, 12, 26),
        'time': time(18, 00)
    }
    assert events[1]['end'] == {
        'date': date(2017, 12, 26),
        'time': time(20, 00)
    }
    assert events[1]['id'] == 'chi_ward_night/201712261800/x/ward_night_ward_5'

    assert events[2]['start'] == {
        'date': date(2018, 1, 23),
        'time': time(18, 00)
    }
    assert events[2]['end'] == {
        'date': date(2018, 1, 23),
        'time': time(20, 00)
    }
    assert events[2]['id'] == 'chi_ward_night/201801231800/x/ward_night_ward_5'


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
