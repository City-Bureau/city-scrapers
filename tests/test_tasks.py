import os
import tasks

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


def test_gen_html():
    FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    test_filenames = [FILES_DIR + '/testspider_articles.html', FILES_DIR + '/testspider_staff.html', FILES_DIR + '/testspider_is-chicago-any-less-segregated.html']
    rendered_filenames = tasks._gen_html(SPIDER_NAME, SPIDER_START_URLS)
    assert rendered_filenames == test_filenames


# @TODO test file open / writing
