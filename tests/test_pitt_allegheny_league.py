import datetime

import pytest
from tests.utils import file_response

from city_scrapers.spiders.pitt_allegheny_league import PittAlleghenyLeagueSpider

spider = PittAlleghenyLeagueSpider()
test_response = file_response('files/pitt_allegheny_league.html')
parsed_items = ([item for item in spider.parse(test_response)
                if isinstance(item, dict)])


def test_name():
    assert parsed_items[0]['name'] == 'ACBA General Membership Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == 'ACBA General Membership Meeting'


def test_start():
    assert (parsed_items[0]['start'] ==
            {'date': datetime.date(2018, 12, 6),
             'time': datetime.time(18, 0),
             'note': ''})


def test_end():
    assert (parsed_items[0]['end'] ==
            {'date': datetime.date(2018, 12, 6),
             'time': datetime.time(21, 0),
             'note': ''})


def test_id():
    assert (parsed_items[0]['id'] ==
            'pitt_allegheny_league/201812061800/'
            'x/acba_general_membership_meeting')


def test_status():
    assert parsed_items[0]['status'] == 'tentative'


def test_location():
    assert parsed_items[0]['location'] == {
        'address': ('Edgewood Country Club, '
                    '100 Churchill Rd, '
                    'Pittsburgh, PA 15235, USA'),
        'name': '',
        'neighborhood': ''
    }


def test_sources():
    assert (parsed_items[0]['sources'] == [{
            'url': ('https://www.google.com/calendar/'
                    'event?eid=NGpqNjBuNzFhdHF2ZGNoNTdmbTAyd'
                    'WhkcmcgYWxvbWNhbGVuZGFyQG0&ctz=America/New_York'),
            'note': ''}])


def test_documents():
    assert (parsed_items[0]['sources'] == [{
            'url': ('https://www.google.com/calendar/'
                    'event?eid=NGpqNjBuNzFhdHF2ZGNoNTdmbTAyd'
                    'WhkcmcgYWxvbWNhbGVuZGFyQG0&ctz=America/New_York'),
            'note': ''}])


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'Committee'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
