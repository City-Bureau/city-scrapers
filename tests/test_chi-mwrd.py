import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.chi_mwrd import Chi_mwrdSpider


#TBD pending text file as testing fixture

test_response = []
with open('tests/files/chi_mwrd_fixture.json') as f:
    for line in f:
        test_response.append(json.loads(line))
spider = Chi_mwrdSpider()
parsed_items = [item for item in spider._parse_events(test_response)]

def test_name():
    assert parsed_items[0]['name'] == 'Board of Commissioners'
    assert parsed_items[2]['name'] == 'Annual Meeting'
