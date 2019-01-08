import json
from datetime import date, time

import pytest
from freezegun import freeze_time

from city_scrapers.constants import CITY_COUNCIL, PASSED, TENTATIVE
from city_scrapers.spiders.chi_citycouncil import ChiCityCouncilSpider

freezer = freeze_time('2018-12-19')
freezer.start()
with open('tests/files/chi_citycouncil.json', 'r') as f:
    test_response = json.load(f)
spider = ChiCityCouncilSpider()
parsed_items = [item for item in spider._parse_events(test_response)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'City Council'


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2019, 1, 23), 'time': time(10, 00), 'note': ''}


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2019, 1, 23),
        'time': time(13, 00),
        'note': 'Estimated 3 hours after start time'
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_citycouncil/201901231000/x/city_council'


def test_classification():
    assert parsed_items[0]['classification'] == CITY_COUNCIL


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE
    assert parsed_items[20]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'Council Chambers, City Hall',
        'address': '121 N LaSalle St Chicago, IL 60602',
        'neighborhood': ''
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url':
            'https://chicago.legistar.com/DepartmentDetail.aspx?ID=12357&GUID=4B24D5A9-FED0-4015-9154-6BFFFB2A8CB4',  # noqa
        'note': ''
    }]


def test_documents():
    assert parsed_items[20]['documents'] == [
        {
            'note': 'Agenda',
            'url':
                'http://media.legistar.com/chic/meetings/937FDFCE-F0EA-452A-B8DF-A0CF51DBD681/Agenda%20Human%20Relations%20N_20181120162153.pdf'  # noqa
        },
        {
            'note': 'Summary',
            'url':
                'http://media.legistar.com/chic/meetings/937FDFCE-F0EA-452A-B8DF-A0CF51DBD681/Corrected%20Summary%20Human%20_20181210125616.pdf'  # noqa
        },
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
