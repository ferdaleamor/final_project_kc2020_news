import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date
import os
import string
import pandas as pd
from datetime import datetime, date, time, timedelta
import numpy as np

path = './data/urls_english.csv'
today = str(date.today())
days_number = 10


class url_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = [
        'https://time.com/'
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

        if response.url.startswith('https://time.com'):
            for article in response.css('h2.title'):
                url = str(article.css('a::attr(href)').extract_first())
                if not url.startswith('https:'):
                    url = 'https://time.com/' + url
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
