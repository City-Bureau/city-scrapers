import os
from unittest.mock import Mock

import pytest
import requests
from freezegun import freeze_time
from lxml.html import fromstring
from scripts import generate_spider, validate_spider
from tests.utils import file_response, read_test_file_content

SPIDER_NAME = 'testspider'
SPIDER_AGENCY_ID = 'Test Spider Board Of Trade And Englightenment'
SPIDER_DOMAINS = ['www.citybureau.org']
SPIDER_START_URLS = [
    'http://www.citybureau.org/articles',
    'http://www.citybureau.org/staff',
    'http://www.citybureau.org/is-chicago-any-less-segregated',
]

session = requests.Session()


def test_classname():
    assert generate_spider._make_classname(SPIDER_NAME) == 'TestspiderSpider'


def test_get_domains():
    assert generate_spider._get_domains(SPIDER_START_URLS) == SPIDER_DOMAINS


def test_render_test():
    test_file_content = read_test_file_content('files/test_testspider.py.example')
    freezer = freeze_time('2018-12-01')
    freezer.start()
    rendered_content = generate_spider._render_content(
        'test.tmpl', name=SPIDER_NAME, domains=SPIDER_DOMAINS, start_urls=SPIDER_START_URLS
    )
    freezer.stop()
    assert test_file_content == rendered_content


def test_render_spider():
    test_file_content = read_test_file_content('files/testspider.py.example')
    rendered_content = generate_spider._render_content(
        'spider.tmpl',
        name=SPIDER_NAME,
        agency_name=SPIDER_AGENCY_ID,
        domains=SPIDER_DOMAINS,
        start_urls=SPIDER_START_URLS
    )
    assert test_file_content.strip() == rendered_content.strip()


def test_gen_html_filenames(monkeypatch):
    FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    test_filenames = [
        FILES_DIR + '/testspider_articles.html',
        FILES_DIR + '/testspider_staff.html',
        FILES_DIR + '/testspider_is-chicago-any-less-segregated.html',
    ]
    patched_fetch_url = Mock()
    patched_fetch_url.side_effect = [
        file_response('files/testspider_articles.html.example'),
        file_response('files/testspider_staff.html.example'),
        file_response('files/testspider_is-chicago-any-less-segregated.html.example'),
    ]
    monkeypatch.setattr('scripts.generate_spider._fetch_url', patched_fetch_url)
    rendered_filenames = generate_spider._gen_html(SPIDER_NAME, SPIDER_START_URLS, session=session)
    assert rendered_filenames == test_filenames
    for f in rendered_filenames:
        os.remove(f)


def test_gen_html_content(monkeypatch):
    patched_fetch_url = Mock()
    patched_fetch_url.return_value = file_response('files/testspider_articles.html.example')
    monkeypatch.setattr('scripts.generate_spider._fetch_url', patched_fetch_url)
    rendered_filenames = generate_spider._gen_html(
        SPIDER_NAME, [SPIDER_START_URLS[0]], session=session
    )
    test_file_content = read_test_file_content('files/testspider_articles.html.example')
    rendered_content = read_test_file_content('files/testspider_articles.html')
    test_dom = fromstring(test_file_content)
    rendered_dom = fromstring(rendered_content)
    test_title = test_dom.xpath('//title')[0].text
    rendered_title = rendered_dom.xpath('//title')[0].text
    assert test_title == rendered_title
    for f in rendered_filenames:
        os.remove(f)


def test_validate_spiders():
    validate_spider.validate_spider('tests/files/validate_spider_fixture.json')


def test_validate_failing_spider():
    with pytest.raises(Exception) as e:
        validate_spider.validate_spider('tests/files/validate_spider_fail_fixture.json')
    assert 'Less than' in str(e)
