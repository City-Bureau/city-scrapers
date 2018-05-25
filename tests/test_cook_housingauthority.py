import pytest

from tests.utils import file_response
from city_scrapers.spiders.cook_housingauthority import Cook_housingAuthoritySpider


test_response = file_response('files/hacc_event.html', 'http://thehacc.org/event/entrepreneurship-boot-camp-session-2-marketing-analysis')
spider = Cook_housingAuthoritySpider()
item = spider._parse_event(test_response)


##### Values designed to vary #####

def test_id():
    assert item['id'] == 'cook_housingauthority/201805111000/x/entrepreneurship_boot_camp_session_2_marketing_plan'

def test_name():
    assert item['name'] == 'Entrepreneurship Boot Camp Session 2, Marketing Plan'

def test_description():
    assert item['description'] == 'Learn how to start and run your own business. See the attached flyer for more details about workshops. FSS participants, Entrepreneurship Boot camp will help you reach your “open my own business” goal. Register today!'

def test_start_time():
    assert item['start_time'].isoformat() == '2018-05-11T10:00:00-05:00'

def test_end_time():
    assert item['end_time'].isoformat() == '2018-05-11T12:00:00-05:00'

def test_parse_date_time_string():
   parsed_meeting_details = spider._parse_raw_details_string('June 12, 2018, 1:00 pm - 2:30 pm 15306 S. Robey Ave.')
   assert parsed_meeting_details['date'] == 'June 12, 2018'
   assert parsed_meeting_details['start_time'] == '1:00 pm'
   assert parsed_meeting_details['end_time'] == '2:30 pm'
   assert parsed_meeting_details['location']['address'] == '15306 S. Robey Ave.'

def test_location():
    assert item['location']== {'address': '15306 S. Robey Ave.',
    'coordinates': {'latitude': None, 'longitude': None},
    'name': None,
    'url': None}

def test_sources():
    assert item['sources'] == [{'note': '',
    'url': 'http://thehacc.org/event/entrepreneurship-boot-camp-session-2-marketing-analysis'}]


##### Static values #####

def test_type():
    assert item['_type'] == 'event'

def test_allday():
    assert item['all_day'] == False

def test_classification():
    assert item['classification'] == 'Not classified'

def test_status():
    assert item['status'] == 'tentative'

def test_timezone():
    assert item['timezone'] == 'America/Chicago'


