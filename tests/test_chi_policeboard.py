from datetime import date, time

import pytest
from tests.utils import file_response
from city_scrapers.spiders.chi_policeboard import ChiPoliceBoardSpider

test_response = file_response('files/chi_policeboard_public_meetings.html', url='https://www.cityofchicago.org/city/en/depts/cpb/provdrs/public_meetings.html')
spider = ChiPoliceBoardSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[8]['name'] == 'Public Meetings of the Police Board'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    expected_description = ("The Police Board holds a regular public meeting once a month. Members of the public are invited to attend and are welcome to address questions or comments to the Board. The Superintendent of Police (or his designee) and the Chief Administrator of the Civilian Office of Police Accountability (or her designee) will be at the meetings. Prior sign-up is required of those wishing to address the Board; contact the Board's office by 4:30 p.m. of the day before the meeting to add your name to the list of speakers. See below for the dates of the regular monthly meetings. Unless otherwise noted, the meetings are on the third Thursday of the month, are scheduled to begin at 7:30 p.m., and take place at Chicago Public Safety Headquarters, 3510 South Michigan Avenue. Also appearing below are links to the transcripts of the meetings and the material made available at the meeting--the \"Blue Book\" that includes the meeting agenda, minutes, statistics on disciplinary matters, and a list of CPD directives issued by the Superintendent.")
    assert item['event_description'] == expected_description


def test_start_time():
    assert parsed_items[8]['start'] == {
        'date': date(2017,9,18),
        'time': time(19,30),
        'note': ''
    }


def test_documents():
    assert parsed_items[8]['documents'] == [
        {'url': 'https://www.cityofchicago.org/content/dam/city/depts/cpb/PubMtgMinutes/BlueBook09182017.pdf',
         'note': 'Blue Book'},
        {'url': 'https://www.cityofchicago.org/content/dam/city/depts/cpb/PubMtgMinutes/PubMtgTranscript09182017.pdf',
         'note': 'Transcript'},
    ]

@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end'] == {'date': None, 'time': None, 'note': ''}


def test_id():
   assert parsed_items[8]['id'] == 'chi_policeboard/201709181930/x/public_meetings_of_the_police_board'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Board'


def test_status():
    assert parsed_items[8]['status'] == 'passed'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'name': None,
        'address': 'Chicago Public Safety Headquarters, 3510 South Michigan Avenue',
        'neighborhood': '',
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.cityofchicago.org/city/en/depts/cpb/provdrs/public_meetings.html',
                                'note': ''}]

