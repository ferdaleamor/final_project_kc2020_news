import scrapy
from scrapy.crawler import CrawlerProcess
import os
import pandas as pd
from datetime import date, timedelta
import numpy as np


def set_url(domain, url):
    today = str(date.today())
    if url is not None:
        if not url.startswith('http'):
            url = domain + str(url)
        if url.startswith(domain):
            print(f"\"{today}\",\"{url}\"", file=filep)

class url_spider(scrapy.Spider):

    name = 'blogspider'
    start_urls = [
        'https://www.20minutos.es',
        'https://www.larazon.es',
        'https://www.publico.es',
        'https://www.abc.es',
        'https://www.lesoir.be',
        'https://www.news.com.au',
        'https://time.com',
        'https://elpais.com',
        'https://www.elmundo.es'
    ]

    def parse(self, response):

        if response.url.startswith('https://www.20minutos.es'):
            for article in response.css('article'):
                url = article.css('header h1 a::attr(href)').extract_first()
                set_url(response.url, url)
                
        elif response.url.startswith('https://www.larazon.es'):
            urls_la_razon = set(response.css('a.story-card__areas__head::attr(href)').getall())
            for url in urls_la_razon:
                set_url(response.url, url)

        elif response.url.startswith('https://www.publico.es'):
            urls_publico = set(response.css('a.page-link::attr(href)').getall())
            for url in urls_publico:
                set_url(response.url, url)
                
        elif response.url.startswith('https://www.elmundo.es'):
            urls_mundo = set(response.css('a.ue-c-cover-content__link::attr(href)').getall())
            for url in urls_mundo:
                set_url(response.url, url)
                              
        elif response.url.startswith('https://elpais.com'):
            for article in response.css('h2.headline'):
                url = article.css('a::attr(href)').extract_first()
                set_url(response.url, url)

        elif response.url.startswith('https://time.com'):
            for article in response.css('h2.title'):
                url = str(article.css('a::attr(href)').extract_first())
                set_url(response.url, url)
                        
        elif response.url.startswith('https://www.abc.es'):
            for article in response.css('article'):
                url = article.css('span h3 a::attr(href)').extract_first()
                set_url(response.url, url)
                  
        elif response.url.startswith('https://www.lesoir.be'):
            for article in response.css('h4.media-heading'):
                url = article.css('a::attr(href)').extract_first()
                set_url(response.url, url)
                  
        elif response.url.startswith('https://www.news.com.au'):
            for article in response.css('h4.heading'):
                url = article.css('a::attr(href)').extract_first()
                set_url(response.url, url)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

path = '../data/urls.csv'
filep = open(path, 'w')
print(f"date,url", file=filep)
process.crawl(url_spider)
process.start()
filep.close()
