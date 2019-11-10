from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response

from city_scrapers.spiders.det_wrecking_examiners import DetWreckingExaminersSpider

test_response = file_response(
    join(dirname(__file__), "files", "det_wrecking_examiners.html"),
    url=(
        'https://www.detroitmi.gov/government/boards/board-wrecking-contractors-examiners/board-wrecking-contractors-meetings'  # noqa
    )
)
spider = DetWreckingExaminersSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_title():
    assert parsed_items[0]['title'] == 'Board of Wrecking Contractors Examiners'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 2, 14, 13)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0][
        'id'
    ] == 'det_wrecking_examiners/201802141300/x/board_of_wrecking_contractors_examiners'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == spider.location


def test_sources():
    assert parsed_items[0][
        'source'
    ] == 'https://www.detroitmi.gov/government/boards/board-wrecking-contractors-examiners/board-wrecking-contractors-meetings'  # noqa


def test_links():
    assert parsed_items[0]['links'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD
