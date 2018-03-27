import json
from datetime import datetime
from tests.utils import read_test_file_content
from documenters_aggregator.pipelines.localExporter import CsvPipeline
from documenters_aggregator.spiders.chi_buildings import Chi_buildingsSpider

testSpider = Chi_buildingsSpider()


def _str_to_datetime(date_string, spider_in=testSpider):
    if not date_string:
        return testSpider
    naive = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    return spider_in._naive_datetime_to_tz(naive)


def load_valid_item():
    fixtures = json.loads(read_test_file_content('files/exporter_fixture.json'))
    valid_item = fixtures[0]
    valid_item['start_time'] = _str_to_datetime(valid_item['start_time'])
    valid_item['end_time'] = _str_to_datetime(valid_item['end_time'])
    return valid_item


valid_item = load_valid_item()
pipeline = CsvPipeline()
pipeline.spider_opened(testSpider)


def test_valid_process_item():
    processed = pipeline.process_item(valid_item, testSpider)
    del processed["scraped_time"]
    expected = {"classification": "Board Meeting", "start_time": "2999-03-13 14:30", "end_time": "2999-03-13 15:30", "source_url": "http://www.pbcchicago.com/events/event/board-meeting-march-13-2999/", "status": "tentative", "description": "N/A", "all_day": 0, "name": "Board Meeting \u2013 March 13, 2999", "location_url": "https://thedaleycenter.com", "location_address": "50 W. Washington Street Chicago, IL 60602", "source_note": "N/A", "location_name": "Second Floor Board Room, Richard J. Daley Center", "agency_name": "Public Building Commission of Chicago", "id": "chi_buildings/299903131430/x/board_meeting_march_13_2999", "_type": "event", "timezone": "America/Chicago"}
    pipeline.spider_closed(testSpider, deleteme=True)
    assert processed == expected
