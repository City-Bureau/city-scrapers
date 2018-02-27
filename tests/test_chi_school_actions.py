import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.chi_school_actions import ChiSchoolActionsSpider


test_response = file_response('files/chi_school_actions.html')
spider = ChiSchoolActionsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Castellanos - Cardenas Community Meetings: Consolidation'


def test_description():
    assert parsed_items[3]['description'] == (
        'Emil G Hirsch Metropolitan High School Community Meetings: Co-location. ' +
        'Documentation: Transition Plan http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=6294, ' +
        'Parent Letter http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=6292, ' +
        'Staff Letter http://schoolinfo.cps.edu/SchoolActions/Download.aspx?fid=6293'
    )


def test_classification():
    assert parsed_items[0]['classification'] == 'Community Meetings: Consolidation'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2018-01-09T18:00:00-06:00'


def test_end_time():
    assert parsed_items[0]['end_time'].isoformat() == '2018-01-09T20:00:00-06:00'


def test_id():
    assert parsed_items[0]['id'] == 'chi_school_actions/201801091800/x/castellanos_cardenas_community_meetings_consolidation'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': '',
        'name': 'Rosario Castellanos ES',
        'address': '2524 S Central Park Ave',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://schoolinfo.cps.edu/SchoolActions/Documentation.aspx',
        'note': ''
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
