import pytest
import json

from freezegun import freeze_time
from documenters_aggregator.spiders.chi_parks import Chi_parksSpider

freezer = freeze_time('2017-10-10 12:00:01')
freezer.start()
test_response = []
with open('tests/files/chi_parks.txt') as f:
    for line in f:
        test_response.append(json.loads(line))
spider = Chi_parksSpider()
parsed_items = [item for item in spider._parse_events(test_response)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Board of Commissioners'
    assert parsed_items[1]['name'] == 'Public Hearing'
    assert parsed_items[3]['name'] == 'Special Meeting'
    assert parsed_items[6]['name'] == 'Budget Forum'


def test_description():
    EXPECTED_DESCRIPTION = ("The Chicago Park District Act provides that the Chicago"
        "Park District shall be governed by a board of seven" 
        "non-salaried Commissioners who are appointed by the Mayor"
        "of the City of Chicago with the approval of the Chicago City"
        "Council. Under the Chicago Park District Code, the Commissioners"
        "have a fiduciary duty to act, vote on all matters, and govern"
        "the Park District in the best interest of the Park District.")
    assert parsed_items[0]['description'] == EXPECTED_DESCRIPTION


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-12-13T15:30:00-06:00'
    assert parsed_items[1]['start_time'].isoformat() == '2017-12-06T15:30:00-06:00'
    assert parsed_items[2]['start_time'].isoformat() == '2017-11-08T15:30:00-06:00'
    assert parsed_items[3]['start_time'].isoformat() == '2017-10-20T13:30:00-05:00'
    assert parsed_items[4]['start_time'].isoformat() == '2017-10-11T15:30:00-05:00'


def test_id():
    assert parsed_items[0]['id'] == 'chi_parks/201712131530/x/board_of_commissioners'
    assert parsed_items[1]['id'] == 'chi_parks/201712061530/x/public_hearing'
    assert parsed_items[3]['id'] == 'chi_parks/201710201330/x/special_meeting'
    assert parsed_items[6]['id'] == 'chi_parks/201709191800/x/budget_forum'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'


def test_status():
    assert parsed_items[0]['status'] == 'tentative'
    assert parsed_items[1]['status'] == 'tentative'
    assert parsed_items[2]['status'] == 'confirmed'
    assert parsed_items[3]['status'] == 'confirmed'
    assert parsed_items[4]['status'] == 'confirmed'
    assert parsed_items[5]['status'] == 'passed'
    assert parsed_items[6]['status'] == 'passed'


def test_location():
    assert parsed_items[1]['location'] == {
        'url': None,
        'address': 'Board Room ADMINISTRATION BUILDING AT 541 NORTH FAIRBANKS COURT, CHICAGO, ILLINOIS 60611 8TH FLOOR BOARD ROOM',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }
    assert parsed_items[2]['location'] == {
        'url': None,
        'address': '8TH FLOOR BOARD ROOM ADMINISTRATION BUILDING AT 541 NORTH FAIRBANKS COURT, CHICAGO, ILLINOIS 60611',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }
    assert parsed_items[3]['location'] == {
        'url': None,
        'address': 'DRINKER, BIDDLE & REATH LLP 191 N. UPPER WACKER DR. STE 3700 CHICAGO, ILLINOIS 60606',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }
    assert parsed_items[4]['location'] == {
        'url': None,
        'address': '2401 N Lake Shore Dr, Chicago, IL 60614 THEATER ON THE LAKE',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }
    assert parsed_items[5]['location'] == {
        'url': None,
        'address': '8TH FLOOR BOARD ROOM',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }
    assert parsed_items[6]['location'] == {
        'url': None,
        'address': 'FOSCO PARK 1312 S. Racine Ave. Chicago, Illinois 60608',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }
    assert parsed_items[7]['location'] == {
        'url': None,
        'address': 'ADMINISTRATION BUILDING AT 541 NORTH FAIRBANKS COURT, CHICAGO, ILLINOIS 60611 8TH FLOOR BOARD ROOM',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }
    assert parsed_items[8]['location'] == {
        'url': None,
        'address': 'Test Training 2',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


def test_sources():
    assert parsed_items[0]['sources'] == [{'note': '', 'url': 'https://chicagoparkdistrict.legistar.com/Calendar.aspx'}]
