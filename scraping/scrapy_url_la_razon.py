import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date

path = './data/' + str(date.today()) + '_url_la_razon.csv'

class la_razon_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.larazon.es/']
    
    def parse(self, response):
        urls = set(response.css('a.story-card__areas__head::attr(href)').getall())
        for url in urls:
            print(f"\"{url}\"", file=filep) 

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(path, 'w')
process.crawl(la_razon_spider)
process.start()
filep.close()
