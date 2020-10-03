import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date, timedelta, datetime
import pandas as pd
from bs4 import BeautifulSoup
import re
import string
import numpy as np
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

write_path = '../data/news.csv'
read_path = '../data/urls.csv'

today = np.datetime64(date.today())
# Obtenemos una lista de las urls a scrapear
df_urls = pd.read_csv(read_path)
urls = list(df_urls['url'])

# Connect databse
cred = credentials.Certificate('../key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Recuperamos las urls scrapeadas de los últimos 10 días en la base de datos
news = db.collection('news').where('date', '>', datetime.today()-timedelta(days=10)).stream()
scrapped_url = []
for new in news:
    new = new.to_dict()
    scrapped_url.append(new['url'])

class news_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = urls
    scrapped_url = scrapped_url
    
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

        new = {
            'date': datetime.timestamp(datetime.now()),
            'url': response.url,
            'headline': headline,
            'text': clean_text,
            'lang': lang
        }
        db.collection('news').add(new)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})
process.crawl(news_spider)
process.start()
