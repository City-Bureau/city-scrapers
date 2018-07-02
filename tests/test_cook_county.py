from datetime import date, time

from tests.utils import file_response
from city_scrapers.spiders.cook_county import Cook_countySpider


test_response = file_response('files/cook_county_event.html',
                              url='https://www.cookcountyil.gov/event/cook-county-zoning-building-committee-6')
spider = Cook_countySpider()
item = spider._parse_event(test_response)


def test_name():
    assert item['name'] == 'ZBA Public Hearing'


def test_start_time():
    assert item['start'] == {
        'date': date(2017, 11, 15),
        'time': time(13, 00),
        'note': ''
    }


def test_end_time():
    assert item['end'] == {
        'date': date(2017, 11, 15),
        'time': time(15, 00),
        'note': '',
    }


def test_id():
   assert item['id'] == 'cook_county/201711151300/x/zba_public_hearing'


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert spider._parse_classification('Board of Commissioners') == 'Board'
    assert spider._parse_classification('Economic Development Advisory Committee') == 'Advisory Committee'
    assert spider._parse_classification('Finance Committee') == 'Committee'
    assert spider._parse_classification('Finance Subcommittee on Litigation') == 'Committee'
    assert spider._parse_classification('Finance Subcommittee on Workers Compensation') == 'Committee'
    assert spider._parse_classification('Committee of Suburban Cook County Commissioners - PACE') == 'Committee'
    assert spider._parse_classification('Rules & Administration Committee') == 'Committee'
    assert spider._parse_classification('Roads & Bridges Committee') == 'Committee'
    assert spider._parse_classification('Zoning & Building Committee') == 'Committee'
    assert spider._parse_classification('Justice Advisory Council') == 'Advisory Committee'
    assert spider._parse_classification('JAC Council Meeting') == 'Advisory Committee'


def test_status():
    assert item['status'] == 'passed'


def test_location():
    assert item['location'] == {
        'neighborhood': None,
        'name': None,
        'address': '69 W. Washington Street Chicago , IL  60602',
    }


def test__type():
    assert item['_type'] == 'event'


def test_sources():
    assert item['sources'] == [{'url': 'https://www.cookcountyil.gov/event/cook-county-zoning-building-committee-6',
                                'note': ''}]


def test_description():
    assert item['event_description'] == (
        'Public Hearing '
        'A public hearing has been scheduled for the Cook County Zoning Board of Appeals on '
        'Wednesday, November 15, 2017, 1:00PM at '
        '69 W. Washington, 22nd Floor Conference Room, Chicago, Illinois 60602.')


def test_documents():
    assert item['documents'] == [{
        'url': 'https://www.cookcountyil.gov/sites/default/files/zba_november_15_agenda.pdf',
        'note': 'ZBA 11-15-2017 Agenda'
    }]
