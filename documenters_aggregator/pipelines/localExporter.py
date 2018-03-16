from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from documenters_aggregator.utils import get_key
import datetime
from os import remove
import subprocess


class CsvPipeline(object):
    """
    Pipeline uses a built in feed exporter from Scrapy currently
    Outputs csv files for local development to the /local_output/ folder
    """

    path = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode("utf-8").rstrip()  + '/documenters_aggregator/local_outputs/'

    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.files = {}

    def spider_opened(self, spider):
        self.stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        self.fname = '{}{}_{}.csv'.format(self.path, spider.name, self.stamp)
        file = open(self.fname, 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = ['agency_name', '_type',
                                          'id', 'name', 'description',
                                          'classification', 'start_time',
                                          'end_time', 'timezone', 'status',
                                          'all_day', 'location_name',
                                          'location_url',
                                          'location_address',
                                          'source_url', 'source_note',
                                          'scraped_time'
                                          ]
        self.exporter.start_exporting()

    def spider_closed(self, spider, deleteme=False):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()
        if deleteme:
            remove(self.fname)

    def process_item(self, item, spider):
        new_item = item.copy()

        # flatten location
        new_item['start_time'] = datetime.datetime.strftime(new_item['start_time'], '%Y-%m-%d %H:%M')
        try:
            new_item['end_time'] = datetime.datetime.strftime(new_item['end_time'], '%Y-%m-%d %H:%M')
        except:
            pass
        new_item['location_url'] = get_key(new_item, 'location.url')
        new_item['location_name'] = get_key(new_item, 'location.name')
        new_item['location_address'] = get_key(new_item, 'location.address')
        new_item['source_url'] = new_item.get('sources', [{'url': ''}])[0].get('url', '')
        new_item['source_note'] = new_item.get('sources', [{'note': ''}])[0].get('note', '')
        new_item['agency_name'] = spider.long_name
        new_item['scraped_time'] = datetime.datetime.strftime(datetime.datetime.strptime(self.stamp, '%Y%m%d_%H%M'), '%Y-%m-%d %H:%M')
        new_item = {k: self._format_values(k, v) for k, v in new_item.items() if k in self.exporter.fields_to_export}

        self.exporter.export_item(new_item)
        return new_item

    def _format_values(self, k, v):
        if ((v is None) or v == '') and (k not in ['start_time', 'end_time']):
            return 'N/A'
        if k == 'location_name':
            return ' '.join([w.capitalize() for w in v.split(' ')])
        if isinstance(v, bool):
            return int(v)
        return v
