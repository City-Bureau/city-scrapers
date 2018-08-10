import pytest
from datetime import date, time

from tests.utils import file_response
from city_scrapers.spiders.wayne_election_commission import WayneElectionCommissionSpider

test_response = file_response('files/wayne_election_commission.html', 'https://www.waynecounty.com/elected/clerk/election-commission.aspx')
spider = WayneElectionCommissionSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Election Commission'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 29),
        'time': None,
        'note': 'Meeting time are given in the "Notice" document'
    }


def test_end():
    assert parsed_items[0]['end'] == {'date': None, 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'wayne_election_commission/201801290000/x/election_commission'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Coleman A. Young Municipal Center, Conference Room 700A',
        'address': '2 Woodward Avenue, Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.waynecounty.com/elected/clerk/election-commission.aspx',
        'note': ''
    }]


def test_documents():
    assert parsed_items[1]['documents'] == [
        {
          'url': 'https://www.waynecounty.com/documents/clerk/wecn2518.pdf',
          'note': 'Notice'
        },
        {
          'url': 'https://www.waynecounty.com/documents/clerk/eca20518.pdf',
          'note': 'Agenda'
        },
        {
          'url': 'https://www.waynecounty.com/documents/clerk/ecm20518.pdf',
          'note': 'Minutes'
        }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Commission'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
