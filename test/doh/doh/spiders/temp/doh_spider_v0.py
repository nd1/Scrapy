import scrapy


class DOHSpider(scrapy.Spider):
    name = "doh"
    start_urls = [
        'http://dc.healthinspections.us/webadmin/DHD_431/web/?a=inspections&alpha=R']

    def parse(self, response):
        # pulls establishment urls from the search page and parses the
        # establishment page
        for item in response.xpath('//h3//a[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]'):
            url = item.xpath('./@href').extract_first()
            if url is not None:
                next_page = response.urljoin(url)
                yield scrapy.Request(next_page, callback=self.parse_insp_links)

    def parse_insp_links(self, response):
        yield {
            'name': response.xpath('//h3//a[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]/text()').extract_first(),
            'establishment_url': response.xpath('//h3//a[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]/@href').extract_first(),
            'address': response.xpath('//*[(@id = "divInspectionSearchResults")]//li/text()')[1].re(r'\r\n\t\t\t\t(.*)'),
            'details': response.xpath('//*[(@id = "divInspectionSearchResults")]//li/text()')[2].re(r'\r\n\t\t\t\tWard: (.*)\r'),
            'category': response.xpath('//*[(@id = "divInspectionSearchResults")]//li/text()')[3].re(r'\r\n\t\t\t\tType: (.*) \r\n\r\n\t\t\t\t')
        }
