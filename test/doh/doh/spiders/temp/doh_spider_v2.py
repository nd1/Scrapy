'''
Learning scrapy/ building a DOH report scraper.
current status: parsing report
have the phone number, however only get inspections for first establishment on R. need to figure out the passing/ yielding/ compilation
'''

import scrapy


class Inspection(scrapy.Item):
    rname = scrapy.Field()
    establishment_url = scrapy.Field()
    address = scrapy.Field()
    neighborhood = scrapy.Field()
    category = scrapy.Field()
    inspection_url = scrapy.Field()
    phone = scrapy.Field()


class DOHSpider(scrapy.Spider):
    name = "doh"
    start_urls = [
        'http://dc.healthinspections.us/webadmin/DHD_431/web/?a=inspections&alpha=3']

    def parse(self, response):
        # pulls establishment urls from the search page and parses the
        # establishment page
        inspections = Inspection()
        for item in response.xpath('//h3//a[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]'):
            url = item.xpath('./@href').extract_first()
            if url is not None:
                next_page = response.urljoin(url)
                request = scrapy.Request(next_page, callback=self.parse_insp_links)
                request.meta['inspections'] = inspections
                return request

    def parse_insp_links(self, response):
        inspections = response.meta['inspections']
        for item in response.xpath('//*[(@id = "divInspectionSearchResultsListing")]//a'):
            inspections['rname'] = response.xpath('//h3//a[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]/text()').extract_first()
            inspections['establishment_url'] = response.xpath('//h3//a[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]/@href').extract_first()
            inspections['address'] = response.xpath('//*[(@id = "divInspectionSearchResults")]//li/text()')[1].re(r'\r\n\t\t\t\t(.*)')
            inspections['neighborhood'] = response.xpath('//*[(@id = "divInspectionSearchResults")]//li/text()')[2].re(r'\r\n\t\t\t\tWard: (.*)\r')
            inspections['category'] = response.xpath('//*[(@id = "divInspectionSearchResults")]//li/text()')[3].re(r'\r\n\t\t\t\tType: (.*) \r\n\r\n\t\t\t\t')
            inspections['inspection_url'] = item.xpath('./@href').extract_first()
            if inspections['inspection_url'] is not None:
                # parse inspection url
                next_page = response.urljoin(inspections['inspection_url'])
                request = scrapy.Request(next_page, callback=self.parse_report)
                request.meta['inspections'] = inspections
                yield request

    def parse_report(self, response):
        inspections = response.meta['inspections']
        inspections['phone'] = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " ))]//div/text()').extract_first()
        return inspections
