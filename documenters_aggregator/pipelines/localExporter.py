from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from documenters_aggregator.utils import get_key
import datetime


class CsvPipeline(object):
    """
    Pipeline uses a built in feed exporter from Scrapy currently
    Outputs csv files for local development to the /local_output/ folder
    """
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.files = {}

    def spider_opened(self, spider):
        stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        path = 'documenters_aggregator/local_outputs/'
        file = open('{}{}_{}.csv'.format(path, spider.name, stamp), 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = ['agency_name',
                                          'id', 'name', 'description',
                                          'classification', 'start_time',
                                          'end_time', 'timezone', 'all_day',
                                          'location_name', 'location_url',
                                          'location_address', 'location_latitude',
                                          'location_longitude', 'url',
                                          ]
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        new_item = item.copy()

        # flatten location
        new_item['location_url'] = get_key(new_item, 'location.url')
        new_item['location_name'] = get_key(new_item, 'location.name')
        new_item['location_address'] = get_key(new_item, 'location.address')
        new_item['location_latitude'] = get_key(new_item, 'location.coordinates.latitude')
        new_item['location_longitude'] = get_key(new_item, 'location.coordinates.longitude')
        new_item['url'] = new_item.get('sources', [{'url': ''}])[0].get('url', '')
        new_item['agency_name'] = spider.long_name
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