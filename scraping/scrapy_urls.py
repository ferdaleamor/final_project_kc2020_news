import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date
import os
import string
import pandas as pd
from datetime import datetime, date, time, timedelta
import numpy as np

path = './data/urls.csv'
today = str(date.today())
days_number = 10


class url_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = [
        'https://www.20minutos.es/',
        'https://www.larazon.es/',
        'https://www.publico.es/'
    ]
    scraped_urls = []
    df_urls = pd.DataFrame(columns=['url','date'])

    def __init__(self):
        # Si el fichero no esta vacío cargamos las urls que ya se han scrapeado y eliminamos las que tienen más de x días
        if not os.stat(path).st_size == 0:
            self.df_urls = pd.read_csv(path)
            self.df_urls['date'] = pd.to_datetime(self.df_urls['date'], format="%Y/%m/%d")
            dates = self.df_urls['date']
            keep = dates > (np.datetime64(date.today() - timedelta(days=days_number)))
            self.df_urls = self.df_urls[keep]
            self.scraped_urls = list(self.df_urls['url'])
    
    def parse(self, response):

        urls = []

        if response.url.startswith('https://www.20minutos.es'):
            for article in response.css('article'):
                url = article.css('header h1 a::attr(href)').extract_first()
                if url.startswith('https://www.20minutos.es') and url not in self.scraped_urls:
                    urls.append(url)
                
        elif response.url.startswith('https://www.larazon.es/'):
            urls_la_razon = set(response.css('a.story-card__areas__head::attr(href)').getall())
            for url in urls_la_razon:
                if url not in self.scraped_urls:
                    urls.append(url)

        elif response.url.startswith('https://www.publico.es/'):
            urls_publico = set(response.css('a.page-link::attr(href)').getall())
            for url in urls_publico:
                if not url.startswith('http'):
                    url = 'https://www.publico.es' + str(url)
                    if url not in self.scraped_urls:
                        urls.append(url)

        for url in urls:
            self.df_urls = self.df_urls.append({'url' : url , 'date' : today} , ignore_index=True)
        
        self.df_urls.to_csv(path, index = False)
            
process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(path, 'w')
process.crawl(url_spider)
process.start()
filep.close()
