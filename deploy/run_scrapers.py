import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import rediswq


if __name__ == '__main__':
    q = rediswq.RedisWQ(
        name=os.getenv('SCRAPER_QUEUE_NAME'),
        host=os.getenv('REDIS_HOST'),
    )
    while not q.empty():
        item = q.lease(block=True, timeout=2)
        if item is not None:
            scraper_name = item.decode('utf-8')
            crawler_process = CrawlerProcess(get_project_settings())
            print(f'Running {scraper_name}')
            crawler_process.crawl(scraper_name)
            crawler_process.start()
            q.complete(item)
        else:
            print('Waiting for work')
    print('Queue empty, exiting')
