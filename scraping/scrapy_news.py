import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import re
import string
import numpy as np
import os

write_path = '../data/news.csv'
read_path = '../data/urls.csv'

today = np.datetime64(date.today())
# Obtenemos una lista de las urls a scrapear
df_urls = pd.read_csv(read_path)
urls = list(df_urls['url'])

def get_news_last_days(path, num_days = 10):
    if not os.path.isfile(path):
        return [] 
    df_news = pd.read_csv(path)
    df_news['scraping_date'] = pd.to_datetime(df_news['scraping_date'], format="%Y/%m/%d")
    dates = df_news['scraping_date']
    keep = dates > (np.datetime64(date.today() - timedelta(days=num_days)))
    df_news = df_news[keep]
    return list(df_news['url'])

scrapped_url = get_news_last_days(write_path, 7)

class news_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = urls
    scrapped_url = scrapped_url
    
    def __init__(self):
        if os.stat(write_path).st_size == 0:
            print(f"scraping_date,url,headline,text,lang", file=filep)

    def parse(self, response):

        list_replace = ['\n', '"', ',']
        extract_text = ""
        lang = 'es'

        if response.url in self.scrapped_url:
            return

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

        elif response.url.startswith('https://elpais.com/'):
            headline = response.css('h1.a_t ::text').get()
            extract_text = 'Suscripción'

        elif response.url.startswith('https://www.elmundo.es/'):
            headline = response.css('h1.ue-c-article__headline ::text').get()
            extract_text = 'Suscripción'

        elif response.url.startswith('https://time.com'):
            headline = response.css('h1.headline').get()
            extract_text = response.css('p').getall()
            lang = 'en'
            
        elif response.url.startswith('https://www.abc.es/'):
            headline = response.css('span.titular::text').get()
            extract_text = response.css('p').getall()
            
        elif response.url.startswith('https://www.lesoir.be/'):
            headline = response.css('article h1::text').get()
            extract_text = response.css('p').getall()
            lang = 'fr'
            
        elif response.url.startswith('https://www.news.com.au/'):
            headline = response.css('h1.story-headline::text').get()
            extract_text = response.css('p').getall()
            lang = 'en'
            
        extract_text = " ".join(extract_text)
        # Elimina todas las etiquetas
        headline = BeautifulSoup(headline, "lxml").text
        clean_text = BeautifulSoup(extract_text, "lxml").text
        # Elimina caracteres problemáticos
        for char in list_replace:
            clean_text = clean_text.replace(char, "").strip()
            headline = headline.replace(char, "").strip()
        print(f"\"{today}\",\"{response.url}\",\"{headline}\",\"{clean_text}\",\"{lang}\"", file=filep)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(write_path, 'a')
process.crawl(news_spider)
process.start()
filep.close()
