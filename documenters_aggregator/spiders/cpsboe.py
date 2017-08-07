# -*- coding: utf-8 -*-
import scrapy

from datetime import datetime
from pytz import timezone

class CpsboeSpider(scrapy.Spider):
  name = 'cpsboe'
  allowed_domains = ['www.cpsboe.org']
  start_urls = ['http://www.cpsboe.org/meetings/planning-calendar']
  domain_url = 'http://www.cpsboe.org'

  def parse(self, response):
    for item in response.css('#content-primary tr')[1:]:
      yield {
        '_type': 'event'
      }
