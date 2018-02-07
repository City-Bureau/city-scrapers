import requests
import os
import time
import json
import pandas as pd

from deploy import ecs
from invoke import Collection, task, run
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
SPIDERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documenters_aggregator/spiders')
TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests/files')
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')

# pty is not available on Windows
try:
    import pty
    assert pty  # prevent pyflakes warning about unused import
    pty_available = True
except ImportError:
    pty_available = False


def quote_list(the_list):
    """Jinja helper to quote list items"""
    return ["'%s'" % element for element in the_list]


# Jinja env
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
env.filters["quote_list"] = quote_list


@task()
def genspider(ctx, name, long_name, start_urls):
    """
    Make a new HTML scraping spider.

    Specify:

        1. Slug / shortname for spider (typically an agency acronym, e.g. `cpl`
           for the Chicago Public Libary).
        2. Long name for spider (e.g. "Chicago Public Library").
        3. URLs to start scraping, separated by commas.

    Example:
    ```
    invoke genspider testspider 'Test Spider Board Of Directors' http://citybureau.org/articles,http://citybureau.org/staff
    ```

    URLs cannot end in `/`.

    """
    start_urls = start_urls.split(',')
    domains = _get_domains(start_urls)
    _gen_spider(name, long_name, domains, start_urls)
    _gen_tests(name)
    _gen_html(name, start_urls)


@task
def runtests(ctx):
    """
    Runs pytest and flake8.
    """
    run('pytest -s', pty=pty_available)
    run('flake8 --ignore E265,E266,E501 --exclude src', pty=pty_available)


def _make_classname(name):
    return '{0}Spider'.format(name.capitalize())


def _gen_spider(name, long_name, domains, start_urls):
    filename = '{0}/{1}.py'.format(SPIDERS_DIR, name)

    with open(filename, 'w') as f:
        content = _render_content('spider.tmpl', name=name, long_name=long_name, domains=domains, start_urls=start_urls)
        f.write(content)

    print('Created {0}'.format(filename))
    return filename


def _gen_tests(name):
    filename = '{0}/test_{1}.py'.format(TESTS_DIR, name)
    with open(filename, 'w') as f:
        content = _render_content('test.tmpl', name=name)
        f.write(content)
    print('Created {0}'.format(filename))
    return filename


def _fetch_url(url, attempt=1, session=requests.Session()):
    """
    Attempt to fetch the specified url. If the request fails, retry it with an
    exponential backoff up to 5 times.
    """
    try:
        # Without this, citybureau.org throttles the first request.
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        r = session.get(url, headers=headers)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        if attempt >= 5:
            return None
        else:
            print(e)
            wait = 2 ** attempt
            print('waiting for {0} seconds'.format(wait))
            time.sleep(wait)
            return _fetch_url(url, attempt + 1)


def _gen_html(name, start_urls, session=requests.Session()):
    """
    urls should not end in /
    """
    files = []
    for url in start_urls:
        r = _fetch_url(url, session=session)
        if r is None:
            continue

        content = r.text.strip()

        url_suffix = url.split('/')[-1]
        if '.' in url_suffix:
            url_suffix = url_suffix.split('.')[-2]
        filename = '{0}/{1}_{2}.html'.format(FILES_DIR, name, url_suffix)

        with open(filename, 'w') as f:
            f.write(content)

        print('Created {0}'.format(filename))
        files.append(filename)

    return files


def _render_content(template, name, long_name=None, domains=None, start_urls=None):
    jinja_template = env.get_template(template)
    classname = _make_classname(name)
    return jinja_template.render(
        name=name, long_name=long_name, domains=domains, classname=classname, start_urls=start_urls)


def _get_domains(start_urls):
    domains = []
    for url in start_urls:
        parsed = urlparse(url)
        if parsed.netloc not in domains:
            domains.append(parsed.netloc)
    return domains


@task
def validate_spider(ctx, spider):
    """
    Validates scraped items from a spider.
    Passes if >=90% of the scraped items
    conform to the schema.
    """
    scraped_items = json.load(open(os.path.join(SCRIPTS_DIR, '{0}.json'.format(spider))))
    validated_items = [{k: v for k, v in item.items() if k.startswith('val_')} for item in scraped_items]
    validation_summary = pd.DataFrame(validated_items).mean()

    print('\n------------Validation Summary for: {0}---------------\n'.format(spider))
    print(validation_summary)

    try:
        assert all([x >= 0.9 for x in validation_summary.tolist()])
    except AssertionError as e:
        message = ('Less than 90% of the scraped items from {0} passed validation. '
            'See the validation summary printed in stdout, and check that the '
            'scraped items conform to the events schema at: '
            'https://city-bureau.gitbooks.io/documenters-event-aggregator/'
            'event-schema.html').format(spider)
        raise Exception(message) from e


# Python invoke namespace (http://docs.pyinvoke.org/en/0.11.0/concepts/namespaces.html#nesting-collections)
ns = Collection()
ns.add_task(genspider)
ns.add_task(runtests)
ns.add_task(validate_spider)
ns.add_collection(ecs, 'ecs')
