import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date

path = './data/' + str(date.today()) + '_url_publico.csv'

class el_mundo_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.publico.es/']
    
    def parse(self, response):
        urls = set(response.css('a.page-link::attr(href)').getall())
        for url in urls:
            if not url.startswith('http'):
                url = 'https://www.publico.es' + str(url)
                print(f"\"{url}\"", file=filep)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(path, 'w')
process.crawl(el_mundo_spider)
process.start()
filep.close()
