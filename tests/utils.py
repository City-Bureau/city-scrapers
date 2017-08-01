import os

from scrapy.http import HtmlResponse, Request


def file_response(file_name, url=None):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the tests directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.

    Based on https://stackoverflow.com/a/12741030, a nice bit of hacking.
    """
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url)
    if not file_name[0] == '/':
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(tests_dir, file_name)
    else:
        file_path = file_name

    file_content = open(file_path, 'r').read()
    body = str.encode(file_content)

    return HtmlResponse(url=url, request=request, body=body)
