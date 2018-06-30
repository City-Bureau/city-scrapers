from datetime import date, time

import pytest
import json

from city_scrapers.spiders.chi_water import Chi_waterSpider

test_response = []
with open('tests/files/chi_water_test.json') as f:
    test_response.extend(json.loads(f.read()))
spider = Chi_waterSpider()
# This line throws error
parsed_items = [item for item in spider._parse_events(test_response)]

##### Test Single Instance #####

def test_name():
    assert parsed_items[0]['name'] == 'Board of Commissioners'

def test_description():
    assert parsed_items[0]['event_description'] == 'no agenda posted'

def test_start_time():
    assert parsed_items[0]['start'] == {
            'date': date(2018, 12, 20),
            'time': time(10, 30, 00),
            'note': ''
            }

def test_id():
   assert parsed_items[0]['id'] == 'chi_water/201812201030/x/board_of_commissioners'

def test_location():
    assert parsed_items[0]['location'] == {
    'address': '100 East Erie Street Chicago, IL 60611',
    'name': 'Board Room',
    'neighborhood': 'River North'
    }

def test_sources():
    assert parsed_items[0]['sources'] == [{'note': '',
   'url': 'https://mwrd.legistar.com/DepartmentDetail.aspx?ID=1622&GUID=5E16B4CD-0692-4016-959D-3F080D6CFFB4'}]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
         'url': 'https://mwrd.legistar.com/MeetingDetail.aspx?ID=570944&GUID=DF1E81E4-2660-42AF-A398-8296420B9341&Options=info&Search=',
         'note': 'meeting details'
         },
    ]

def test_documents_with_agenda():
    assert parsed_items[-2]['documents'] == [
        {'url': 'https://mwrd.legistar.com/MeetingDetail.aspx?ID=437015&GUID=639F6AB7-6E76-4429-B6F5-FCEB3DC609C5&Options=info&Search=',
         'note': 'meeting details'},
        {'url': 'https://mwrd.legistar.com/View.ashx?M=A&ID=437015&GUID=639F6AB7-6E76-4429-B6F5-FCEB3DC609C5',
         'note': 'agenda'}
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_name_not_study_session(item):
    assert item['name'] != 'Study Session'


def test_status():
    assert parsed_items[-1]['status'] == 'passed'

##### Parameterized Tests #####

@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] is 'event'

@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False

@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == ''

@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end'] == {
        'date': None,
        'time': None,
        'note': ''
    }



