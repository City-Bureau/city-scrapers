import os
import tasks

from lxml.html import fromstring
from tests.utils import read_test_file_content

SPIDER_NAME = 'testspider'
SPIDER_URL = 'citybureau.org'
SPIDER_START_URLS = ['http://www.citybureau.org/articles',
                     'http://www.citybureau.org/staff',
                     'http://www.citybureau.org/is-chicago-any-less-segregated']


def test_classname():
    assert tasks._make_classname(SPIDER_NAME) == 'TestspiderSpider'


def test_render_test():
    test_file_content = read_test_file_content('files/test_testspider.py.example')
    rendered_content = tasks._render_content(SPIDER_NAME, SPIDER_URL, 'test.tmpl')
    assert test_file_content == rendered_content


def test_render_spider():
    test_file_content = read_test_file_content('files/testspider.py.example')
    rendered_content = tasks._render_content(SPIDER_NAME, SPIDER_URL, 'spider.tmpl')
    assert test_file_content == rendered_content


def test_gen_html_filenames():
    FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    test_filenames = [FILES_DIR + '/testspider_articles.html', FILES_DIR + '/testspider_staff.html', FILES_DIR + '/testspider_is-chicago-any-less-segregated.html']
    rendered_filenames = tasks._gen_html(SPIDER_NAME, SPIDER_START_URLS)
    assert rendered_filenames == test_filenames

    if rendered_filenames == test_filenames:
        for f in rendered_filenames:
            split_f = f.split('/files/')
            os.rename(f, split_f[0] + '/files/tmp/' + split_f[1])


def test_gen_html_content():
    rendered_filenames = tasks._gen_html(SPIDER_NAME, SPIDER_START_URLS)
    test_file_content = read_test_file_content('files/testspider_articles.html.example')
    rendered_content = read_test_file_content('files/testspider_articles.html')
    test_dom = fromstring(test_file_content)
    rendered_dom = fromstring(rendered_content)
    test_title = test_dom.xpath('//title')[0].text
    rendered_title = rendered_dom.xpath('//title')[0].text
    assert test_title == rendered_title

    if test_title == rendered_title:
        for f in rendered_filenames:
            split_f = f.split('/files/')
            os.rename(f, split_f[0] + '/files/tmp/' + split_f[1])


# @TODO test file open / writing
