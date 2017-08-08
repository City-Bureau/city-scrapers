from invoke import task
from jinja2 import Environment, FileSystemLoader

import os


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
SPIDERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documenters_aggregator/spiders')
TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


@task
def genspider(ctx, name, domain):
    """
    Make a new HTML scraping spider
    """
    spider_filename = _gen_spider(name, domain)
    print('Created {0}'.format(spider_filename))

    test_filename = _gen_tests(name, domain)
    print('Created {0}'.format(test_filename))


def _make_classname(name):
    return '{0}Spider'.format(name.capitalize())


def _gen_spider(name, domain):
    filename = '{0}/{1}.py'.format(SPIDERS_DIR, name)
    with open(filename, 'w') as f:
        content = _render_content(name, domain, 'spider.tmpl')
        f.write(content)
    return filename


def _gen_tests(name, domain):
    template = env.get_template('test.tmpl')
    filename = '{0}/test_{1}.py'.format(TESTS_DIR, name)
    with open(filename, 'w') as f:
        content = _render_content(name, domain, 'test.tmpl')
        f.write(content)
    return filename


def _render_content(name, domain, template):
    jinja_template = env.get_template(template)
    classname = _make_classname(name)
    return jinja_template.render(name=name, domain=domain, classname=classname)

