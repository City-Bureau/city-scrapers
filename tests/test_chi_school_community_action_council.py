from datetime import datetime
import pytest

from tests.utils import file_response
from city_scrapers.spiders.chi_school_community_action_council import Chi_school_community_action_councilSpider

test_response = file_response('files/chi_school_community_action_council_CAC.html', url='http://cps.edu/FACE/Pages/CAC.aspx')
spider = Chi_school_community_action_councilSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_len():
    current_month_number = datetime.today().month
    assert len(parsed_items) == (13 - current_month_number)*8  # len varies depending on the month that the spider is run


def test_name():
    assert parsed_items[0]['name'] == 'Austin Community Action Council'


def test_start_time():
    # this test will fail if it is run after June 2018
    assert parsed_items[0]['start_time'].isoformat() == '2018-06-12T17:30:00'

def test_end_time():
    # this test will fail if it is run after June 2018
    assert parsed_items[0]['end_time'].isoformat() == '2018-06-12T20:30:00'


# def test_id():
#    assert parsed_items[0]['id'] == \
#           'chi_school_community_action_council/201805081730/x/austin_community_action_council'


def test_location():
    assert parsed_items[0]['location'] == {
            'url': None,
            'name': ' Michele Clark HS ',
            'address': '5101 W Harrison St.',
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == "Community Action Councils, or CACs, consist of 25-30 voting members who are " \
                                  "directly involved in developing a strategic plan for educational success within " \
                                  "their communities. CAC members include parents; elected officials; faith-based " \
                                  "institutions, health care and community-based organizations; Local School" \
                                  " Council (LSC) members; business leaders; educators and school administrators; " \
                                  "staff members from Chicago's Sister Agencies; community residents; " \
                                  "and students. There are nine CACs across Chicago. Each works to empower the " \
                                  "community they serve to lead the improvement of local quality education."



@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'http://cps.edu/FACE/Pages/CAC.aspx',
                                'note': ''}]

@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Education'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
