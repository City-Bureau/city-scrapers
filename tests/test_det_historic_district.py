from datetime import datetime

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.det_historic_district import DetHistoricDistrictSpider

freezer = freeze_time('2019-03-17')
freezer.start()

test_response = file_response(
    'files/det_historic_district.html',
    url='https://detroitmi.gov/events/regular-historic-district-commission-hdc-meeting-2',
)
spider = DetHistoricDistrictSpider()
item = spider.parse_event_page(test_response)

freezer.stop()


def test_title():
    assert item['title'] == 'Historic District Commission - Regular Meeting'


def test_description():
    assert item['description'] == ''


def test_start():
    assert item['start'] == datetime(2019, 2, 13, 17, 30)


def test_end():
    assert item['end'] == datetime(2019, 2, 13, 20, 30)


def test_time_notes():
    assert item['time_notes'] == 'Estimated 3 hour duration'


def test_id():
    assert item[
        'id'
    ] == 'det_historic_district/201902131730/x/historic_district_commission_regular_meeting'  # noqa


def test_status():
    assert item['status'] == PASSED


def test_location():
    assert item['location'] == {
        "name": 'Erma L. Henderson Auditorium',
        'address': '2 Woodward Avenue, Suite 1300 Detroit, MI 48226'
    }


def test_source():
    assert item[
        'source'
    ] == 'https://detroitmi.gov/events/regular-historic-district-commission-hdc-meeting-2'  # noqa


def test_links():
    assert item['links'] == [{
        'href':
            'https://detroitmi.gov/sites/detroitmi.localhost/files/events/2019-02/2019_02%2013_HDC%20FINAL%20Agenda_0.pdf',  # noqa
        'title': '2019_02 13_HDC FINAL Agenda.pdf'
    }]


def test_classification():
    assert item["classification"] == COMMISSION


def test_all_day():
    assert item["all_day"] is False
