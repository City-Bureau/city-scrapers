import os
import string
import sys
import time
from datetime import date
from urllib.parse import urlparse

import requests
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
SPIDERS_DIR = os.path.join(BASE_DIR, 'city_scrapers', 'spiders')
TESTS_DIR = os.path.join(BASE_DIR, 'tests')
FILES_DIR = os.path.join(TESTS_DIR, 'files')


def quote_list(the_list):
    """Jinja helper to quote list items"""
    return ["'%s'" % element for element in the_list]


# Jinja env
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
env.filters["quote_list"] = quote_list


def genspider(name, agency_name, start_urls):
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

    """ # noqa
    start_urls = start_urls.split(',')
    domains = _get_domains(start_urls)
    _gen_spider(name, agency_name, domains, start_urls)
    _gen_tests(name)
    _gen_html(name, start_urls)


def _make_classname(name):
    return '{}Spider'.format(string.capwords(name, sep='_').replace('_', ''))


def _gen_spider(name, agency_name, domains, start_urls):
    filename = '{0}/{1}.py'.format(SPIDERS_DIR, name)

    with open(filename, 'w') as f:
        content = _render_content(
            'spider.tmpl',
            name=name,
            agency_name=agency_name,
            domains=domains,
            start_urls=start_urls
        )
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
        headers = {
            'user-agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'  # noqa
        }
        r = session.get(url, headers=headers)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        if attempt >= 5:
            return None
        else:
            print(e)
            wait = 2**attempt
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
        filename = '{0}/{1}.html'.format(FILES_DIR, name)

        url_suffix = url.split('/')[-1]
        if '.' in url_suffix:
            url_suffix = url_suffix.split('.')[-2]
        if url_suffix:
            filename = '{0}/{1}_{2}.html'.format(FILES_DIR, name, url_suffix)
        else:
            filename = '{0}/{1}.html'.format(FILES_DIR, name)

        with open(filename, 'w') as f:
            f.write(content)

        print('Created {0}'.format(filename))
        files.append(filename)

    return files


def _render_content(template, name, agency_name=None, domains=None, start_urls=None):
    jinja_template = env.get_template(template)
    classname = _make_classname(name)
    return jinja_template.render(
        name=name,
        agency_name=agency_name,
        domains=domains,
        classname=classname,
        start_urls=start_urls,
        date_str=date.today().strftime('%Y-%m-%d'),
    )


def _get_domains(start_urls):
    domains = []
    for url in start_urls:
        parsed = urlparse(url)
        if parsed.netloc not in domains:
            domains.append(parsed.netloc)
    return domains


if __name__ == '__main__':
    genspider(*sys.argv[1:])
