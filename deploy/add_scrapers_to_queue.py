import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import rediswq


if __name__ == '__main__':
    q = rediswq.RedisWQ(
        name=os.getenv('SCRAPER_QUEUE_NAME'),
        host=os.getenv('REDIS_HOST'),
    )
    crawler_process = CrawlerProcess(get_project_settings())
    for spider_name in crawler_process.spider_loader.list():
        q.put(spider_name)
