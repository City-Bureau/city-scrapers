import requests
import os
import time

from invoke import task, run
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
SPIDERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documenters_aggregator/spiders')
TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests/files')

# pty is not available on Windows
try:
    import pty
    assert pty  # prevent pyflakes warning about unused import
    pty_available = True
except ImportError:
    pty_available = False


def quote_list(the_list):
    return ["'%s'" % element for element in the_list]


env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
env.filters["quote_list"] = quote_list


@task()
def genspider(ctx, name, start_urls):
    """
    Make a new HTML scraping spider. Specify urls separated by commas.

    Example:
    ```
    invoke genspider testspider http://citybureau.org/articles,http://citybureau.org/staff
    ```

    URLs cannot end in `/`.

    """
    start_urls = start_urls.split(',')
    domains = _get_domains(start_urls)
    _gen_spider(name, domains, start_urls)
    _gen_tests(name)
    _gen_html(name, start_urls)


@task
def runtests(ctx):
    """
    Runs pytest, pyflakes, and pep8.
    """
    run('pytest', pty=pty_available)
    run('pyflakes .', pty=pty_available)
    run('pep8 --ignore E265,E266,E501 .', pty=pty_available)


def _make_classname(name):
    return '{0}Spider'.format(name.capitalize())


def _gen_spider(name, domains, start_urls):
    filename = '{0}/{1}.py'.format(SPIDERS_DIR, name)

    with open(filename, 'w') as f:
        content = _render_content('spider.tmpl', name=name, domains=domains, start_urls=start_urls)
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


def _fetch_url(url, attempt=1):
    """
    Attempt to fetch the specified url. If the request fails, retry it with an
    exponential backoff up to 5 times.
    """
    try:
        r = requests.get(url)
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


def _gen_html(name, start_urls):
    """
    urls should not end in /
    """
    files = []
    for url in start_urls:
        r = _fetch_url(url)
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


def _render_content(template, name, domains=None, start_urls=None):
    jinja_template = env.get_template(template)
    classname = _make_classname(name)
    return jinja_template.render(
        name=name, domains=domains, classname=classname, start_urls=start_urls)


def _get_domains(start_urls):
    domains = []
    for url in start_urls:
        parsed = urlparse(url)
        if parsed.netloc not in domains:
            domains.append(parsed.netloc)
    return domains
