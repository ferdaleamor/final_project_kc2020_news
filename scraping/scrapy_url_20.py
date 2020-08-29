import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date

path = './data/' + str(date.today()) + '_url_20min.csv'

class veinte_minutos_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.20minutos.es/']
    
    def parse(self, response):
        for article in response.css('article'):
            url = article.css('header h1 a::attr(href)').extract_first()
            if url.startswith('https://www.20minutos.es'):
                print(f"\"{url}\"", file=filep)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(path, 'w')
process.crawl(veinte_minutos_spider)
process.start()
filep.close()
