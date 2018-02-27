import calendar
from datetime import datetime
from pytz import timezone

from tests.utils import file_response
from documenters_aggregator.spiders.cook_pubhealth import Cook_pubhealthSpider


test_response = file_response('files/cook_pubhealth_321.html', 'http://www.cookcountypublichealth.org/events-view/321')
spider = Cook_pubhealthSpider()
item = spider.parse_event_page(test_response)


def test_name():
    assert item['name'] == 'Fresh Food Market: Robbins Health Center'


def test_description():
    expected_description = (
        'This summer, Fresh Food Markets will be hosted weekly, '
        '10:00 a.m. - 2:00 p.m. at three Cook County Health and Hospital System health '
        'centers in South Suburban Cook County.Robbins Health Center, 13450 W. Kedzie., Robbins.'
        'Black Oaks Center, a local nonprofit, is partnering with CCHHS to make fresh fruits and '
        'vegetables available for sale at CCHHS health centers. Cash, credit, and Link cards '
        '(SNAP/EBT/food stamps) are accepted as forms of payment. Persons using their SNAP/Link '
        'card benefits to purchase will receive a Link Match Coupon, as part of the Link Up '
        'Illinois program, good towards the next purchase of fruits and/or vegetables.If you '
        'have Medicaid or receive a medical card, you may be eligible for SNAP. Our partners '
        'at the Greater Chicago Food Depository can assist with SNAP applications. Visit their'
        'websiteor call 773-843-5416 to reach their Benefits Outreach team.')
    expected_description = ''.join(expected_description.split())
    item_no_whitespace = ''.join(item['description'].split())
    assert item_no_whitespace == expected_description


def test_start_time():
    assert item['start_time'].isoformat() == '2018-09-08T10:00:00-05:00'


def test_end_time():
    assert item['end_time'].isoformat() == '2018-09-08T14:00:00-05:00'


def test_id():
    assert item['id'] == 'cook_pubhealth/201809081000/321/fresh_food_market_robbins_health_center'


def test_classification():
    assert item['classification'] == 'Fresh Food Market'


def test_location():
    assert item['location'] == {
        'url': None,
        'name': None,
        'address': 'Robbins Health Center 13450 W. Kedzie, Robbins, IL',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test_all_day():
    assert item['all_day'] is False


def test_timezone():
    assert item['timezone'] == 'America/Chicago'


def test_status():
    assert item['status'] == 'tentative'


def test__type():
    assert item['_type'] == 'event'


def test__make_date():
    today_weekday = calendar.day_name[datetime.today().weekday()]
    expected_date = '{0} {1}'.format(datetime.today().isoformat()[:10], "2:00 PM")
    expected_date = datetime.strptime(expected_date, '%Y-%m-%d %I:%M %p')
    tz = timezone('America/Chicago')
    spider._make_date(today_weekday, "2:00 PM") == tz.localize(expected_date).isoformat()


def test_sources():
    assert item['sources'] == [{'note': '', 'url': 'http://www.cookcountypublichealth.org/events-view/321'}]
