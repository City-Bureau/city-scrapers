from datetime import date, time

import pytest

from tests.utils import file_response
from city_scrapers.spiders.chi_landmark_commission import ChiLandmarkCommissionSpider

test_response = file_response(
    'files/chi_landmark_commission_landmarks_commission.html',
    'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/landmarks_commission.html'
)
spider = ChiLandmarkCommissionSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_meeting_count():
    # 12 mtgs / yr * 10 yrs + 3 extra (May 2018, March 2014, June 2013)
    assert len(parsed_items) == 123


def test_unique_id_count():
    assert len(set([item['id'] for item in parsed_items])) == 123


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_name():
    assert parsed_items[0]['name'] == 'Commission on Chicago Landmarks'


def test_description():
    assert parsed_items[0]['event_description'] == \
           "The Commission on Chicago Landmarks is responsible for recommending buildings, " \
           "structures, sites and districts for legal protection as official Chicago " \
           "landmarks. Staffed by the Historic Preservation Division of the Department " \
           "of Planning and Development (DPD), the commission is also responsible for " \
           "reviewing proposed alterations to existing landmarks and districts, as well " \
           "as proposed demolitions of structures considered to be historically or " \
           "architecturally significant. Established in 1968, the commission has 9 " \
           "members that are appointed by the mayor with City Council consent. Meetings " \
           "are generally held on the first Thursday of every month at " \
           "City Hall, 121 N. La Salle St., Room 201-A."


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 11),
        'time': time(12, 45),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 1, 11),
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_landmark_commission/201801111245/x/commission_on_chicago_landmarks'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'City Hall',
        'address': '121 N. LaSalle St., Room 201-A'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/landmarks_commission.html',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/zlup/Historic_Preservation/Minutes/CCLJan2018Minutes.pdf',
            'note': 'Minutes'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Commission'
