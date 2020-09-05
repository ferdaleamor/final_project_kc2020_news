import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup
import re
import string
import numpy as np
import os

write_path = './data/news.csv'
read_path = './data/urls.csv'

today = np.datetime64(date.today())
df_urls = pd.read_csv(read_path)
df_urls['date'] = pd.to_datetime(df_urls['date'], format="%Y/%m/%d")
dates = df_urls['date']
keep = dates == today
df_urls = df_urls[keep]
urls = list(df_urls['url'])


class news_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = urls
    
    def __init__(self):
        if os.stat(read_path).st_size == 0:
            print(f"scraping_date,url,headline,text", file=filep)

    def parse(self, response):

        list_replace = ['\n', '"', ',']
        extract_text = ""
        if response.url.startswith('https://www.publico.es/'):
            headline = response.css('h1').get()
            # Elimina las etiquetas span y su contenido
            headline = re.sub(r'<span>.+</span>','',headline)
            extract_text = response.css('p.pb-article-item-iteration').getall()
        
        elif response.url.startswith('https://www.20minutos.es'):
            headline = response.css('main section div h1 ::text').extract_first().strip()
            extract_text = response.css('section article div p ::text').getall()

        elif response.url.startswith('https://www.larazon.es/'):
            headline = response.css('h1.headline').get()
            extract_text = response.css('p.body-components__text').getall()

        elif response.url.startswith('https://time.com'):
            headline = response.css('h1.headline').get()
            extract_text = response.css('p').getall()
            
        elif response.url.startswith('https://www.abc.es/'):
            headline = response.css('span.titular::text').get()
            extract_text = response.css('p').getall()
            
        elif response.url.startswith('https://www.lesoir.be/'):
            headline = response.css('article h1::text').get()
            extract_text = response.css('p').getall()
            
        elif response.url.startswith('https://www.news.com.au/'):
            headline = response.css('h1.story-headline::text').get()
            extract_text = response.css('p').getall()
            

        extract_text = " ".join(extract_text)
        # Elimina todas las etiquetas
        headline = BeautifulSoup(headline, "lxml").text
        clean_text = BeautifulSoup(extract_text, "lxml").text
        # Elimina caracteres problemáticos
        for char in list_replace:
            clean_text = clean_text.replace(char, "").strip()
            headline = headline.replace(char, "").strip()
        print(f"\"{today}\",\"{response.url}\",\"{headline}\",\"{clean_text}\"", file=filep)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(write_path, 'a')
process.crawl(news_spider)
process.start()
filep.close()
