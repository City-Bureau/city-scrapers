# -*- coding: utf-8 -*-
import urllib
from urllib.parse import urljoin

import requests
import scrapy
from dateutil.parser import parse

from city_scrapers.spider import Spider


class DetCityCouncilSpider(Spider):
    name = 'det_city_council'
    agency_id = 'Detroit City Council'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    start_urls = ['http://www.detroitmi.gov/Government/City-Council/City-Council-Sessions']

    def start_requests(self):
        r = scrapy.FormRequest(
            url=self.start_urls[0],
            formdata={
                # 'RadAJAXControlID': 'dnn_ctr8319_Events_UP',
                # 'ScriptManager_TSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en:1dfc24a8-f1c6-47eb-a669-f28ac03160f2:ea597d4b:b25378d2;Telerik.Web.UI, Version=2013.2.717.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:e3f2cc69-ba1e-40db-bc46-4dec0d4c670e:16e4e7cd:f7645509:ed16cbdc:24ee1bba:19620875:874f8ea2:f46195d3:cda80b3:383e4ce8:8674cba1:7c926187:b7778d6c:c08e9f8a:59462f1:a51ee93e:2003d0b8:1e771326:aa288e2d',
                # 'StylesheetManager_TSSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en:1dfc24a8-f1c6-47eb-a669-f28ac03160f2:ea597d4b:b25378d2;Telerik.Web.UI, Version=2013.2.717.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:e3f2cc69-ba1e-40db-bc46-4dec0d4c670e:16e4e7cd:f7645509:ed16cbdc:24ee1bba:19620875:874f8ea2:f46195d3:cda80b3:383e4ce8:8674cba1:7c926187:b7778d6c:c08e9f8a:59462f1:a51ee93e:2003d0b8:1e771326:aa288e2d',
                # '__ASYNCPOST': 'true',
                '__EVENTARGUMENT': 'V6756',
                '__EVENTTARGET': 'dnn$ctr8319$Events$EventMonth$EventCalendar',
                # 'dnn$ctr8319$Events$EventMonth$SelectLocation$btnUpdate': None,
                # 'dnn$ctr8319$Events$EventMonth$SelectCategory$btnUpdate': None,
                # 'dnn_ctr8319_Events_EventMonth_SelectCategory_ddlCategories_ClientState': '{"logEntries":[],"value":"","text":"15 items checked","enabled":true,"checkedIndices":[9,10,11,12,13,14,15,16,17,18,19,20,21,22,50],"checkedItemsTextOverflows":false}',
                # 'dnn_ctr8319_Events_EventMonth_SelectLocation_ddlLocations_ClientState': '{"logEntries":[],"value":"","text":"All","enabled":true,"checkedIndices":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49],"checkedItemsTextOverflows":false}',
                # 'dnn_ctr8319_Events_EventMonth_dpGoToDate_ClientState': '{"minDateStr":"1753-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00"}',
                # 'dnn_ctr8319_Events_EventMonth_dpGoToDate_dateInput_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"2018-08-09-00-00-00","valueAsString":"2018-08-09-00-00-00","minDateStr":"1753-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":"8/9/2018"}',
                # 'ScriptManager': 'dnn$ctr8319$dnn$ctr8319$Events_UPPanel|dnn$ctr8319$Events$EventMonth$EventCalendar',
            }
        )
        # r = requests.get(self.start_urls[0])
        # r = scrapy.http.TextResponse(url=r.url, body=r.content)
        # r = scrapy.FormRequest.from_response(
        #     r,
        #     formname='Form',
        #     formdata={
        #         'RadAJAXControlID': 'dnn_ctr8319_Events_UP',
        #         'ScriptManager_TSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en:1dfc24a8-f1c6-47eb-a669-f28ac03160f2:ea597d4b:b25378d2;Telerik.Web.UI, Version=2013.2.717.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:e3f2cc69-ba1e-40db-bc46-4dec0d4c670e:16e4e7cd:f7645509:ed16cbdc:24ee1bba:19620875:874f8ea2:f46195d3:cda80b3:383e4ce8:8674cba1:7c926187:b7778d6c:c08e9f8a:59462f1:a51ee93e:2003d0b8:1e771326:aa288e2d',
        #         'StylesheetManager_TSSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en:1dfc24a8-f1c6-47eb-a669-f28ac03160f2:ea597d4b:b25378d2;Telerik.Web.UI, Version=2013.2.717.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:e3f2cc69-ba1e-40db-bc46-4dec0d4c670e:16e4e7cd:f7645509:ed16cbdc:24ee1bba:19620875:874f8ea2:f46195d3:cda80b3:383e4ce8:8674cba1:7c926187:b7778d6c:c08e9f8a:59462f1:a51ee93e:2003d0b8:1e771326:aa288e2d',
        #         '__ASYNCPOST': 'true',
        #         '__EVENTARGUMENT': 'V6756',
        #         '__EVENTTARGET': 'dnn$ctr8319$Events$EventMonth$EventCalendar',
        #         'dnn$ctr8319$Events$EventMonth$SelectLocation$btnUpdate': None,
        #         'dnn$ctr8319$Events$EventMonth$SelectCategory$btnUpdate': None,
        #         'dnn_ctr8319_Events_EventMonth_SelectCategory_ddlCategories_ClientState': '{"logEntries":[],"value":"","text":"15 items checked","enabled":true,"checkedIndices":[9,10,11,12,13,14,15,16,17,18,19,20,21,22,50],"checkedItemsTextOverflows":false}',
        #         'dnn_ctr8319_Events_EventMonth_SelectLocation_ddlLocations_ClientState': '{"logEntries":[],"value":"","text":"All","enabled":true,"checkedIndices":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49],"checkedItemsTextOverflows":false}',
        #         'dnn_ctr8319_Events_EventMonth_dpGoToDate_ClientState': '{"minDateStr":"1753-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00"}',
        #         'dnn_ctr8319_Events_EventMonth_dpGoToDate_dateInput_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"2018-08-09-00-00-00","valueAsString":"2018-08-09-00-00-00","minDateStr":"1753-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":"8/9/2018"}',
        #         'ScriptManager': 'dnn$ctr8319$dnn$ctr8319$Events_UPPanel|dnn$ctr8319$Events$EventMonth$EventCalendar',
        #     },
        #     dont_click=True,
        # )
        return [r]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        prev_call_count = response.meta.get('prev_call_count', 0)
        # if prev_call_count < 2:
        # yield from self._next_month(response)
        yield from self._generate_requests(response)

    # @staticmethod
    # def _next_month(response):
    #     prev_call_count = response.meta.get('prev_call_count', 0)
    #     if prev_call_count < 2:
    #         form_params_xpath = "//td[@class='EventNextPrev'][2]/a/@href"
    #         event_target, event_argument = response.xpath(form_params_xpath).re(r'\'(.*?)\'')
    #         yield scrapy.FormRequest.from_response(
    #             response,
    #             formname='Form',
    #             formdata={'__EVENTTARGET': event_target, '__EVENTARGUMENT': event_argument},
    #             meta={'prev_call_count': prev_call_count + 1},
    #         )

    def _generate_requests(self, response):
        anchor_xpath = "//a[contains(@id, 'ctlEvents')]"
        anchors = response.xpath(anchor_xpath)
        anchors = [anchor for anchor in anchors if 'RECESS' not in anchor.xpath('text()').extract_first().upper()]
        if len(anchors) == 0:
            raise ValueError
        rb = response.request.body.decode(response.request.encoding)
        out = '\n'.join(sorted(rb.split("&")))
        with open('/Users/mathewkrump/mine', 'w') as f:
            f.write(out)
        for a in anchors:
            yield response.follow(a, self._parse_item)

    def _parse_item(self, response):
        name = self._parse_name(response)
        description = self._parse_description(response)
        start = self._get_date(response, "Start Date")
        end = self._get_date(response, "End Date")
        location = self._get_location(response)
        documents = self._parse_documents(response)

        data = {
            '_type': 'event',
            'name': name,
            'event_description': description,
            'classification': 'Committee',
            'start': start,
            'end': end,
            'all_day': False,
            'location': location,
            'documents': documents,
            'sources': [{'url': response.url, 'note': ''}],
        }
        data['id'] = self._generate_id(data)
        data['status'] = self._generate_status(data, text='')
        yield data

    @staticmethod
    def _parse_description(response):
        try:
            description_xpath = '//div[span[contains(., "Description")]]/following-sibling::div//p/text()'
            description = response.xpath(description_xpath).extract_first().strip()
            return description
        except:
            return ''

    @staticmethod
    def _parse_name(response):
        name_xpath = '//span[@class="Head"]/text()'
        name_text = response.xpath(name_xpath).extract_first()
        name_value = name_text.split('-')[0].strip()
        return name_value

    @staticmethod
    def _get_location(response):
        location_xpath = '//div[span[contains(., "Location")]]/following-sibling::div[1]/span/a/text()'
        location_text = response.xpath(location_xpath).extract_first()
        if 'YOUNG MUNICIPAL CENTER' in location_text.upper():
            return {
                'neighborhood': '',
                'name': 'Coleman A. Young Municipal Center',
                'address': '2 Woodward Detroit, MI 48226'
            }
        return {'neighborhood': '', 'name': '', 'address': location_text}

    @staticmethod
    def _get_date(response, contains):
        date_xpath = '//div[span[contains(., "{}")]]/following-sibling::div[1]/span[1]/text()'.format(contains)
        date_text = response.xpath(date_xpath).extract_first()
        if date_text:
            dt = parse(date_text)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        return {'date': None, 'time': None, 'note': ''}

    def _parse_documents(self, response):
        documents_selector = '//div[span[contains(., "Description")]]/following-sibling::div//a'
        anchors = response.xpath(documents_selector)
        documents = []
        for a in anchors:
            documents_text = a.xpath('text()').extract_first()
            documents_link = a.xpath('@href').extract_first()
            url = urljoin(response.url, documents_link)
            documents.append({'url': url, 'note': documents_text})
        return documents
