import json
from scrapy.exporters import JsonItemExporter
import datetime


class JsonWriterPipeline(object):

    def __init__(self):
        self.stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        self.fname = './documenters_aggregator/local_outputs/{}_{}.json'.format('output', self.stamp)
        self.file = open(self.fname, 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
