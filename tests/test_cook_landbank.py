import pytest
from tests.utils import file_response
from city_scrapers.spiders.cook_landbank import Cook_landbankSpider

file = file_response('files/cook_landbank.json')
spider = Cook_landbankSpider()

test_response = file
parsed_items = list(spider.parse(test_response))


def test_name():
    assert parsed_items[0]['name'] == 'CCLBA Finance Committee Meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_event_description(item):
    assert item['event_description'] == ("The Cook County Land Bank Authority Finance Committee will meet on Wednesday, September 13th, 2017 at the hour of 10:00 AM in the Cook County Administration Building located at 69 W. Washington St., 22nd Floor, Conference Room ‘A’, Chicago, Illinois, to consider the following: AGENDA (CLICK HERE FOR PDF) 1. Call to Order and Roll Call 2. Public Speakers (Please note each registered speaker is asked to limit comments to 3 minutes) 3. FY 2016 Audit – Presentation By Washington, Pittman, & McKeever 4. CCLBA’s FY2018 Proposed Budget (Cassidy Harper/Robert Rose) 5. Update regarding CCLBA’s Line of Credit (Rob Rose) 6. Finance Report (Cassidy Harper) 7. Consent Agenda Approval of June 29, 2017 Cook County Land Bank Finance Committee meeting minutes. 8. Chairman’s Report (Director Calvin Holmes) 9. Adjournment Committee Chair: Holmes Members: Jenkins, Ostenburg, Sherwin")


def test_start():
    assert parsed_items[0]['start'].isoformat() == '2017-09-13T10:00:00-05:00'


def test_end():
    assert parsed_items[0]['end'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


# def test_id():
#    assert parsed_items[0]['id'] == 'cook_landbank/201709131000/3381/cclba_finance_committee_meeting'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'Not classified'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': 'http://www.cookcountylandbank.org/',
        'name': None,
        'address': "Cook County Administration Building, 69 W. Washington St., 22nd Floor, Conference Room 'A', Chicago, IL 60602",
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.cookcountylandbank.org/events/cclba-finance-committee-meeting-09132017/',
        'note': "Event Page",
    }]


def test__type():
    assert parsed_items[0]['_type'] == 'event'
