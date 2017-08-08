import pytest
import tasks

from tests.utils import read_test_file_content

SPIDER_NAME = 'testspider'
SPIDER_URL = 'citybureau.org'


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


# @TODO test file open / writing
