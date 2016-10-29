'''
status- only parsing report pages. working. need to build out parse.
'''

import scrapy


class Inspection(scrapy.Item):
    inspection_url = scrapy.Field()
    rname = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    phone = scrapy.Field()
    email = scrapy.Field()
    insp_date = scrapy.Field()
    time_in = scrapy.Field()
    time_out = scrapy.Field()


class DOHSpider(scrapy.Spider):
    name = "doh"
    start_urls = [
        'http://dc.healthinspections.us/webadmin/DHD_431/web/?a=inspections&alpha=3']

    def parse(self, response):
        inspections = Inspection()
        # starts at 3
        for item in response.xpath('//*[(@id = "divInspectionSearchResultsListing")]//a'):
            url = item.xpath('./@href').extract_first()
            inspections['inspection_url'] = url
            next_page = response.urljoin(url)
            request = scrapy.Request(next_page, callback=self.parse_report)
            request.meta['inspections'] = inspections
            yield request

    def parse_report(self, response):
        inspections = response.meta['inspections']
        inspections['rname'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "times", " " ))]//table//tr[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " ))]').re(r'\xa0(.*)\r\n\t\t\t\t\t\t\t')
        inspections['address'] = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " ))]').re(r'\xa0(.*)\r\n\t\t\t\t\t\t\t')
        inspections['city'] = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]').re(r'\xa0(.*)\r\n\t\t\t\t\t\t\t')
        inspections['phone'] = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " ))]//div/text()').extract_first()
        inspections['email'] = response.xpath('//td[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " ))]').re(r'\xa0(.*)\r\n\t\t\t\t\t\t\t')[-1]
        inspections['insp_date'] = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 5) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " ))]//div/text()').re(r'\xa0(.*)')[:3]
        inspections['time_in'] = response.xpath('//sup | //tr[(((count(preceding-sibling::*) + 1) = 5) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " ))]//div/text()').re(r'\xa0(.*)')[3:5]
        inspections['time_out'] = response.xpath('//sup | //tr[(((count(preceding-sibling::*) + 1) = 5) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "container", " " ))]//div/text()').re(r'\xa0(.*)')[5:7]
        return inspections
