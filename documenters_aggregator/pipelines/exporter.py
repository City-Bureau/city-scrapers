from scrapy.exporters import CsvItemExporter


class CsvPipeline(object):
    """
    Pipeline uses a built in feed exporter from Scrapy currently
    Outputs csv files for local development to the /local_output/ folder
    """
    def __init__(self):
        self.file = open("documenters_aggregator/local_outputs/outputtest.csv", 'wb')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def create_valid_csv(self, item):
        for key, value in item.items():
            is_string = (isinstance(value, str))
            if (is_string and ("," in value.encode('utf-8'))):
                item[key] = "\"" + value + "\""

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
                    
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()