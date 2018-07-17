from datetime import date, time

import pytest

from tests.utils import file_response
from city_scrapers.spiders.chi_community_development import ChiCommunityDevelopmentSpider

test_response = file_response(
    'files/chi_development_community_developmentcommission.html',
    'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/community_developmentcommission.html'
)
spider = ChiCommunityDevelopmentSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_meeting_count():
    # 12 mtgs / yr * 10 yrs + 3 extra (2016)
    assert len(parsed_items) == 123


def test_unique_id_count():
    assert len(set([item['id'] for item in parsed_items])) == 123


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_name():
    assert parsed_items[0]['name'] == 'Community Development Commission'


def test_description():
    assert parsed_items[0]['event_description'] == \
           "The Community Development Commission (CDC) was established by the Chicago City Council in 1992 to assume " \
           "the duties of the former Commercial District Development Commission and the Department of Urban Renewal. " \
           "The CDC reviews and recommends action on the provision of Tax Increment Financing (TIF) to assist private " \
           "redevelopment projects; the designation of new TIF districts and Redevelopment Areas; the sale of " \
           "City-owned property located in TIF districts and Redevelopment Areas; and the appointment of members to " \
           "Community Conservation Councils. The CDC is comprised of 15 members appointed by the Mayor and confirmed " \
           "by the City Council."


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 16),
        'time': time(1, 00),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 1, 16),
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_community_development/201801160100/x/community_development_commission'


def test_status():
   assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'City Hall',
        'address': '121 N. LaSalle St., Room 201A'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/community_developmentcommission.html',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/dcd/agendas/CDC_Minutes_Jan_2018.pdf',
            'note': 'Minutes'
        }
    ]
    assert parsed_items[1]['documents'] == [
        {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/dcd/agendas/CDC_Minutes_Feb_2018.pdf',
            'note': 'Minutes'
        }
    ]
    assert parsed_items[2]['documents'] == [
        {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/dcd/agendas/CDC_March_2018_Minutes.pdf',
            'note': 'Minutes'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Commission'
