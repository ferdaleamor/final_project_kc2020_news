import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date

url_list = []
path = './data/' + str(date.today()) + '_url_20min.csv'

class veinte_minutos_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.20minutos.es/']
    
    def parse(self, response):

        for article in response.css('article'):
            url = article.css('header h1 a:nth-child(1)::attr(href)').extract_first().strip()
            url_list.append(url)
            print(f"\"{url}\"", file=filep)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(path, 'w')
process.crawl(veinte_minutos_spider)
process.start()
filep.close()
