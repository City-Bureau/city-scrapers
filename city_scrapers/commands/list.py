from scrapy.commands.list import Command as ExistingListCommand


class Command(ExistingListCommand):
    def run(self, args, opts):
        for s in sorted(self.crawler_process.spider_loader.list()):
            cls = self.crawler_process.spider_loader.load(s)
            print('{0: <6} |  {1}'.format(s, cls.long_name))
