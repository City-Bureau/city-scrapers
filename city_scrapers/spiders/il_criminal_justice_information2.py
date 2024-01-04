import scrapy
from scrapy_playwright.page import PageMethod
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

class IlCriminalJusticeInformationSpider(CityScrapersSpider):
    name = "il_criminal_justice_information2"
    agency = "Illinois Criminal Justice Information Authority"
    timezone = "America/Chicago"
    location = {
        "name": "Illinois Criminal Justice Information Authority",
        "address": "300 W Adams St, Suite 200, Chicago, IL 60606",
    }
    
    def start_requests(self):
        url = "https://icjia.illinois.gov/news/meetings/"
        yield scrapy.Request(url, meta={
                'playwright': True,
                'playwright_include_page': True,
                'errback': self.errback,
                'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.v-data-table__wrapper > table > tbody'),
                    ],

            })

    async def parse(self, response):
        """.
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        page = response.meta["playwright_page"]

        rows = await page.query_selector_all('table > tbody > tr')
        row_count = len(rows)
        for row_no in range(1, row_count + 1):
            row_el = await page.query_selector(f'table > tbody > tr:nth-child({row_no})')
            print("row no.", row_no)
            title_element = await row_el.query_selector('td:nth-child(4) > div')
            if title_element:
                title_text = await title_element.inner_text()
                print("Title:", title_text)
            await row_el.click()
            detail_row_el = await page.query_selector(".v-data-table__expanded.v-data-table__expanded__content > td > div")
            if detail_row_el:
                detail_row_text = await detail_row_el.inner_text()
                print("Detail:", detail_row_text)
            
        await page.close()


    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
