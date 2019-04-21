import re
from collections import defaultdict
from datetime import datetime, timedelta
from urllib import parse

import scrapy
from city_scrapers_core.items import Meeting


class DetCityMixin:
    timezone = 'America/Detroit'
    allowed_domains = ['detroitmi.gov']
    dept_cal_id = None # Agency URL param when filtering calendar page with "Department" drop down
    dept_doc_id = '' # Agency URL param when filtering documents page with "Department" drop down
    agency_cal_id = None  # Agency URL param when filtering the calendar page
    agency_doc_id = None  # Agency URL param (or list of params) when filtering the documents page
    start_days_prev = 120  # Number of days before today to start searching
    doc_query_param_dept = 'field_department_target_id[0][target_id]'
    doc_query_param = 'field_department_target_id_1[0][target_id]'

    def __init__(self, *args, **kwargs):
        """Initialize spider document link list and doc date defaultdict for matching"""
        self.document_links = []
        self.document_date_map = defaultdict(list)
        super().__init__(*args, **kwargs)

    @property
    def start_urls(self):
        """Start with documents if provided, otherwise from events"""
        if self.agency_doc_id:
            agency_doc_id = self.agency_doc_id
            if isinstance(agency_doc_id, list):
                agency_doc_id = agency_doc_id[0]
            return [
                'https://detroitmi.gov/documents?{}={}&{}={}'.format(self.doc_query_param_dept, \
                    self.dept_doc_id, self.doc_query_param, agency_doc_id)
            ]
        else:
            return [self.get_event_start_url()]

    def get_event_start_url(self):
        """Get the initial calendar filter URL based on start_days_prev and agency_cal_id"""
        start_date = (datetime.now() - timedelta(days=self.start_days_prev)).strftime('%Y-%m-%d')

        # If no department filter is specified, use the "Government" filter only
        if (self.dept_cal_id is None):
            return (
                'https://detroitmi.gov/Calendar-and-Events?'
                'field_start_value={}&term_node_tid_depth_1={}'
            ).format(start_date, self.agency_cal_id)

        # Else filter add the Department filter
        else:
            return (
                'https://detroitmi.gov/Calendar-and-Events?'
                'field_start_value={}&term_node_tid_depth={}&term_node_tid_depth_1={}'
            ).format(start_date, self.dept_cal_id, self.agency_cal_id)


    def parse(self, response):
        """Set parse method based on the response URL"""
        if 'Calendar-and-Events' in response.url:
            return self.parse_event_list(response)
        elif '/events/' in response.url:
            return self.parse_event_page(response)
        else:
            return self.parse_documents_page(response)

    def parse_documents_page(self, response):
        """Parse the document search result page"""
        # Add links if available
        self.document_links.extend(self._parse_document_links(response))
        # Continue iterating through results if not at the end
        next_url = self._response_next_url(response)
        # Create next_url for documents if additional agency doc IDs
        if not next_url and isinstance(self.agency_doc_id, list):
            next_url = self._replace_agency_doc_param(response.url)
        if next_url:
            yield scrapy.Request(
                response.urljoin(next_url), callback=self.parse_documents_page, dont_filter=True
            )
        else:
            # If no results are available, create the mapping of docs and dates, request events
            self._create_document_date_map()
            yield scrapy.Request(
                self.get_event_start_url(), callback=self.parse_event_list, dont_filter=True
            )

    def parse_event_list(self, response):
        """Iterate through the event results page results"""
        for event in response.css('.view-content .article-title a::attr(href)'):
            event_url = event.extract()
            yield scrapy.Request(
                response.urljoin(event_url), callback=self.parse_event_page, dont_filter=True
            )
        next_url = self._response_next_url(response)
        if next_url:
            yield scrapy.Request(
                response.urljoin(next_url), callback=self.parse_event_list, dont_filter=True
            )

    def parse_event_page(self, response):
        """Yield a meeting from an individual event page"""
        start = self._parse_start(response)
        end, has_end = self._parse_end(response, start)
        meeting = Meeting(
            title=self._parse_title(response),
            description=self._parse_description(response),
            classification=self._parse_classification(response),
            start=start,
            end=end,
            time_notes=self._parse_time_notes(has_end),
            all_day=False,
            location=self._parse_location(response),
            links=self._parse_links(response, start),
            source=self._parse_source(response),
        )
        meeting['status'] = self._get_status(meeting)
        meeting['id'] = self._get_id(meeting)
        return meeting

    def _parse_title(self, response):
        """Parse the title, removing the date if included"""
        title_text = response.css('.page-header > span::text').extract_first()
        return re.sub(r'( - )?\d{1,4}-\d{1,2}-\d{1,4}$', '', title_text.strip()).strip()

    def _parse_description(self, response):
        """Parse the event description"""
        return ' '.join(response.css('article.description > *::text').extract())

    def _parse_start(self, response):
        """Parse the start datetime"""
        date_str = response.css('.date time::attr(datetime)').extract_first()
        time_str = ''.join(response.css('article.time::text').extract()).strip()
        time_split = time_str.split('-')
        start_str = time_split[0].strip()
        start_str = re.sub(r'\.|from', '', start_str.lower())
        if 'am' not in start_str and 'pm' not in start_str:
            if len(time_split) > 1:
                end_str = time_split[1].lower().replace('.', '')
                if 'am' in end_str or 'pm' in end_str:
                    start_str += 'am' if 'a' in end_str else ' pm'
            # Create int by getting the first number (excluding minutes)
            start_int = int(re.search(r'\d+', start_str).group())
            start_nums = re.search(r'[\d:]+', start_str).group()
            start_str = start_nums + ('pm' if start_int < 8 else 'am')
        start_date = datetime.strptime(date_str[:10], '%Y-%m-%d').date()
        return datetime.combine(start_date, self._parse_time_str(start_str))

    def _parse_end(self, response, start):
        """Parse the end datetime, returning a boolean indicating whether it was scraped"""
        time_str = ''.join(response.css('article.time::text').extract()).strip()
        time_split = time_str.split('-')
        if len(time_split) > 1:
            end_str = time_split[1].strip()
            return (
                datetime.combine(start.date(), self._parse_time_str(end_str)),
                True,
            )
        else:
            return start + timedelta(hours=3), False

    def _parse_time_notes(self, has_end):
        """Parse time notes based on whether the end datetime was scraped or a default"""
        return '' if has_end else 'Estimated 3 hour duration'

    def _parse_location(self, response):
        """Parse the location name and address from the page"""
        loc_info = response.css('.location-info')
        return {
            'name': loc_info.css('p strong span::text').extract_first(),
            'address': loc_info.css('.field--name-field-address::text').extract_first()
        }

    def _parse_links(self, response, start):
        """Parse links pulled from documents and the agenda"""
        links = self.document_date_map[start.date()]
        for agenda in response.css('.agenda-min-pres .file-link a'):
            agenda_url = response.urljoin(agenda.xpath('@href').extract_first())
            title = agenda.xpath('./text()').extract_first()
            if title.strip().startswith('Agenda'):
                title = 'Agenda'
            links.append({'title': re.sub(r'\s+', ' ', title).strip(), 'href': agenda_url})
        return links

    def _parse_source(self, response):
        """Parse the event source URL"""
        return response.url

    def _parse_document_links(self, response):
        """Parse document links from the document search results page"""
        document_links = []
        for link in response.css('.view-site-documents .view-content .field-content a'):
            document_links.append({
                'title': link.xpath('./text()').extract_first(),
                'href': response.urljoin(link.xpath('@href').extract_first()),
            })
        return document_links

    def _parse_time_str(self, time_str):
        """Handle parsing a variety of time strings"""
        time_fmt = '%I:%M%p'
        time_str = re.sub(r'\s+', '', re.sub(r'from|\.', '', time_str.lower())).replace('o', '0')
        if ':' not in time_str:
            time_fmt = '%I%p'
        return datetime.strptime(time_str, time_fmt).time()

    def _response_next_url(self, response):
        """Return the next URL for filter results if it's available"""
        return response.css('ul.pagination .pager__item--next a::attr(href)').extract_first()

    def _create_document_date_map(self):
        """Create a mapping of document dates and documents to match with meetings"""
        for doc_link in self.document_links:
            date_str = None
            date_fmt = '%Y-%m-%d'
            date_match = re.search(r'^\d{4}[ -]\d{1,2}[ -]\d{1,2}', doc_link['title'].strip())
            if date_match:
                date_str = date_match.group().replace(' ', '-')
            if not date_match:
                doc_title = doc_link['title'].replace('.', '')
                date_fmt = '%B %d, %Y' #change to 'b' instead of 'B' to work
                date_match = re.search(r'[a-zA-Z]{3,9} \d{1,2},? \d{4}', doc_title)
            if date_match:
                if not date_str:
                    date_str = date_match.group()
                doc_date = datetime.strptime(date_str, date_fmt).date()
                self.document_date_map[doc_date].append(doc_link)

    def _replace_agency_doc_param(self, response_url):
        """Replace agency_doc_id and page in query parameters for next_url"""
        scheme, netloc, path, query_string, fragment = parse.urlsplit(response_url)
        query_dict = parse.parse_qs(query_string)
        if self.doc_query_param in query_dict:
            url_agency_doc_id = query_dict[self.doc_query_param][0]
            doc_id_index = self.agency_doc_id.index(url_agency_doc_id)
            if doc_id_index < len(self.agency_doc_id) - 1:
                query_dict[self.doc_query_param] = [self.agency_doc_id[doc_id_index + 1]]
                query_dict.pop('page', None)
                qs = parse.urlencode(query_dict, doseq=True)
                return parse.urlunsplit((scheme, netloc, path, qs, fragment))
