from scrapy.commands.list import Command as ExistingListCommand


class Command(ExistingListCommand):
    def run(self, args, opts):
        for s in sorted(self.crawler_process.spider_loader.list()):
            cls = self.crawler_process.spider_loader.load(s)
            if hasattr(cls, 'long_name'):
                agency_name = cls.long_name
            else:
                agency_name = cls.agency_id
            print('{0: <6} |  {1}'.format(s, agency_name))
