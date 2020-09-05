import scrapy
from scrapy.crawler import CrawlerProcess
import json
import os
import string
import pandas as pd
from datetime import datetime, date, time, timedelta
import numpy as np

path = './data/urls.csv'
today = str(date.today())
days_number = 10
scraped_urls = []

df_urls = pd.read_csv(path)
df_urls['date'] = pd.to_datetime(df_urls['date'], format="%Y/%m/%d")
dates = df_urls['date']
keep = dates > (np.datetime64(date.today() - timedelta(days=days_number)))
df_urls = df_urls[keep]
scraped_urls = list(df_urls['url'])


class url_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = [
        'https://www.20minutos.es/',
        'https://www.larazon.es/',
        'https://www.publico.es/',
        'https://www.abc.es/',
        'https://www.lesoir.be/',
        'https://www.news.com.au/'
    ]

    
    def parse(self, response):

        global df_urls
        global scraped_urls

        urls = []

        if response.url.startswith('https://www.20minutos.es'):
            for article in response.css('article'):
                url = article.css('header h1 a::attr(href)').extract_first()
                if url.startswith('https://www.20minutos.es') and url not in scraped_urls:
                    urls.append(url)
                
        elif response.url.startswith('https://www.larazon.es/'):
            urls_la_razon = set(response.css('a.story-card__areas__head::attr(href)').getall())
            for url in urls_la_razon:
                if url not in scraped_urls:
                    urls.append(url)

        elif response.url.startswith('https://www.publico.es/'):
            urls_publico = set(response.css('a.page-link::attr(href)').getall())
            for url in urls_publico:
                if not url.startswith('http'):
                    url = 'https://www.publico.es' + str(url)
                    if url not in scraped_urls:
                        urls.append(url)

        elif response.url.startswith('https://time.com'):
            for article in response.css('h2.title'):
                url = str(article.css('a::attr(href)').extract_first())
                if not url.startswith('https:'):
                    url = 'https://time.com/' + url
                if url not in scraped_urls:
                    urls.append(url)
                        
        elif response.url.startswith('https://www.abc.es/'):
            for article in response.css('article'):
                url = article.css('span h3 a::attr(href)').extract_first()
                if url is not None:
                    if not url.startswith('http'):
                        url = 'https://www.abc.es' + str(url)
                    if url.startswith('https://www.abc.es') and url not in scraped_urls:
                        urls.append(url)
                  
        elif response.url.startswith('https://www.lesoir.be/'):
            for article in response.css('h4.media-heading'):
                url = article.css('a::attr(href)').extract_first()
                if url is not None:
                    if not url.startswith('http'):
                        url = 'https://www.lesoir.be' + str(url)
                    if url.startswith('https://www.lesoir.be') and url not in scraped_urls:
                            urls.append(url)
                  
        elif response.url.startswith('https://www.news.com.au/'):
            for article in response.css('h4.heading'):
                url = article.css('a::attr(href)').extract_first()
                if url is not None:
                    if not url.startswith('http'):
                        url = 'https://www.news.com.au/' + str(url)
                    if url.startswith('https://www.news.com') and url not in scraped_urls:
                            urls.append(url)
            

        for url in urls:
            df_urls = df_urls.append({'url' : url , 'date' : today} , ignore_index=True)
        
        df_urls.to_csv(path, index = False)
            
process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(path, 'w')
process.crawl(url_spider)
process.start()
filep.close()
