import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date

path = './data/' + str(date.today()) + '_url_el_mundo.csv'

class el_mundo_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.elmundo.es/']
    
    def parse(self, response):
        urls = response.css('a.ue-c-cover-content__link::attr(href)').getall()
        for url in urls:
            print(f"\"{url}\"", file=filep)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(path, 'w')
process.crawl(el_mundo_spider)
process.start()
filep.close()
