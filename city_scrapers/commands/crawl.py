from scrapy.commands.crawl import Command as ExistingCrawlCommand
from scrapy.exceptions import UsageError


class Command(ExistingCrawlCommand):
    def run(self, args, opts):
        if len(args) < 1:
            raise UsageError()
        elif len(args) > 1:
            raise UsageError(
                "running 'scrapy crawl' with more than one spider is no longer supported"
            )
        spname = args[0]

        self.crawler_process.crawl(spname, **opts.spargs)
        crawler = list(self.crawler_process.crawlers)[0]
        self.crawler_process.start()

        error_count = crawler.stats.get_value('log_count/ERROR')
        exception_count = crawler.stats.get_value('downloader/exception_count')
        drop_count = crawler.stats.get_value('item_dropped_count')

        if error_count or exception_count or drop_count:
            self.exitcode = 1
