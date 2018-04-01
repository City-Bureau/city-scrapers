import json
from scrapy.exporters import JsonItemExporter, CsvItemExporter
import datetime


def generate_file_name(file_format):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    file_name = './documenters_aggregator/local_outputs/{}_{}.{}'.format('output',timestamp, file_format)
    return file_name


class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open(generate_file_name('json'), 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class CsvWriterPipeline(object):

    def __init__(self):
        self.file = open(generate_file_name('csv'), 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
